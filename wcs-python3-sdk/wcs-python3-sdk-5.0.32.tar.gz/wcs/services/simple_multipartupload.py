#!/usr/bin/python
## -*- coding: utf-8 -*-

import os,sys
import time,datetime
from os.path import expanduser
from multiprocessing import Lock
from multiprocessing.dummy import Pool as ThreadPool
from wcs.commons.config import Config
from wcs.commons.http import _post
from wcs.commons.logme import debug,warning,error
from wcs.commons.util import readfile,GetUuid
from wcs.commons.util import urlsafe_base64_encode,https_check
from wcs.commons.error_deal import  WcsSeriveError
from wcs.services.uploadprogressrecorder import UploadProgressRecorder
#config_file = os.path.join(expanduser("~"), ".wcscfg")

class Simple_MultipartUpload(object):
    """分片上传类
    分片上传引入了块和片，一个文件由一到多个块组成，而每个块由一到多个片组成，块大小和片大小是可配的。块之间可以并发上传也可以顺序上传，块内的片之间只能顺序上传
    分片上传通过导入UploadProgressRecorder实现断点续传
    Attributes:
        url: 上传域名
        token: 鉴权token
        path: 源文件路径
        size: 源文件大小
        key: 源文件名
        blocknum: 源文件块数目
        results: 读取上传进度到这个变量
        uploadBatch: upload id
        progress: 当前上传进度
        recorder: UploadProgressRecorder的实例
        cfg: Config的实例
        concurrency: 块并发度
        block_size: 块大小
        bput_size: 片大小
        
    """   
    def __init__(self,url):
        self.url = url
        self.token = ''
        self.path = ''
        self.size = 0
        self.key = ''
        self.blocknum = 0
        self.results = []
        self.uploadBatch = ''
        self.progress = 0
        self.recorder = None
        #self.cfg = Config(config_file)
        self.cfg = Config()
        try:
            self.concurrency = int(self.cfg.concurrency)
            self.block_size = int(self.cfg.block_size)
            self.bput_size = int(self.cfg.bput_size)
        except ValueError as e:
            error(u"Invalid value,please check .wcscfg file")
            sys.exit()

    def __need_retry(self,code):
        if code == 500 or code == -1:
            return True
        return False

    def _define_config(self,path,token):
        self.token = token
        self.path = path
        self.size = os.path.getsize(self.path)
        self.key = os.path.basename(path)
        if self.size % self.block_size != 0:
            self.blocknum = int(self.size/self.block_size + 1)
        else:
            self.blocknum = int(self.size/self.block_size)
        self.results = []
        self.progress = 0
        self.modify_time = time.time() 

    def _record_upload_progress(self, result, size):
        result_dict = dict(zip(['offset', 'code', 'ctx'], result))
        result_dict['size'] = size
        if result_dict['code'] == 200:
            #lock.acquire()
            self.progress += size
            debug('Current block size: %d, total upload size: %d' % (int(size), self.progress))
            #lock.release()
        self.recorder.set_upload_record(result_dict['offset'],result_dict)

    def todo_record_upload_progress(self, w_result_list):
        '''
        :param w_result_list: 多线程使用的list数据（result，size）
        :return:
        '''
        return self._record_upload_progress(w_result_list[0],w_result_list[1])

    def _records_parse(self, upload_id):
        records = self.recorder.get_upload_record()
        offsetlist = [i * (self.block_size) for i in range(0,self.blocknum)]
        debug(records)
        if records:
            self.uploadBatch = records['uploadBatch']
            self.results = records['upload_record']
            for record in self.results:
                try:
                    record = eval(record)
                except SyntaxError as e:
                    debug('Get ctx/offset fail,error ctx/offset:{0}'.format(record))

                except Exception as exc_e:
                    debug('Get ctx/offset fail,errorinfo:{0}'.format(exc_e))

                if record['code'] == 200:
                    offsetlist.remove(record['offset'])
                    blockid = record['offset']/self.block_size
                    if blockid < self.blocknum - 1:
                        self.progress += self.block_size
                    else:              
                        self.progress += self.size - (blockid * self.block_size)       
        return offsetlist
    
    def _make_bput_post(self, ctx, bputnum, bput_next):
        url = https_check(self.__bput_url(ctx, bputnum*self.bput_size))
        headers = self.__generate_headers()
        return _post(url=url, headers=headers, data=bput_next)

    def __bput_url(self, ctx, offset):
        return '{0}/bput/{1}/{2}'.format(self.url, ctx, offset)

    def __block_url(self,size,blocknum):
        return '{0}/mkblk/{1}/{2}'.format(self.url, size, int(blocknum))

    def __file_url(self):
        url = ['{0}/mkfile/{1}'.format(self.url, self.size)]
        #if self.params:
        #    for k, v in self.params.items():
        #        url.append('x:{0}/{1}'.format(k, urlsafe_base64_encode(v)))
        url = '/'.join(url)
        return url

    def __generate_headers(self):
        headers = {'Authorization':self.token}
        headers['uploadBatch'] = self.uploadBatch
        return headers

    def _mlk_url(self, offset):
        blockid = offset/self.block_size
        if blockid < self.blocknum - 1:
            size = self.block_size
        else:
            size = int(self.size - (blockid * self.block_size))
        return self.__block_url(int(size), blockid), size

    def _make_block(self, offset):
        url,size = self._mlk_url(offset)
        url = https_check(url)
        headers = self.__generate_headers()        
        try:
            mkblk_retries = int(self.cfg.mkblk_retries)
        except ValueError as e:
            warning('parameter mkblk_retries is invalid, so use default value 3')
            mkblk_retries = 3
        with open(self.path, 'rb') as f:
            bput = readfile(f, offset, self.bput_size)
            blkcode, blktext,_ = _post(url=url,headers=headers, data=bput)
            while mkblk_retries and self.__need_retry(blkcode):
                debug('make block fail.retry upload')
                blkcode, blktext,_ = _post(url=url, headers=headers, data=bput)
                mkblk_retries -= 1
            if blkcode != 200:
                result = [offset, blkcode, blktext['message']]
                debug('make block fail,code :{0},message :{1}'.format(blkcode, blktext))
            else:
                result = self._make_bput(f, blktext['ctx'], offset)
        #self._record_upload_progress(result,size)
        return blkcode,result,size
    
    def _make_bput(self, f, ctx, offset):
        bputnum = 1
        offset_next = offset + self.bput_size
        bput_next = readfile(f, offset_next, self.bput_size)
        bputcode = 200
        bputtext = {'ctx' : ctx}
        try:
            bput_retries = int(self.cfg.bput_retries)
        except ValueError as e:
            warning('parameter bput_retries is invalid, so use default value 3')
            bput_retries = 3
        while bput_next and bputnum < self.block_size/self.bput_size:
            bputcode, bputtext, _ = self._make_bput_post(ctx, bputnum, bput_next)
            while bput_retries and self.__need_retry(bputcode):
                debug('bput fail.retry upload')
                bputcode, bputtext, _ = self._make_bput_post(ctx, bputnum, bput_next)
                bput_retries -= 1
            if bputcode != 200:
                return offset, bputcode, bputtext['message']
            ctx = bputtext['ctx']
            offset_next = offset + bputtext['offset']
            bput_next = readfile(f, offset_next, self.bput_size)
            bputnum += 1
        return offset, bputcode, bputtext['ctx']
 
    def _is_complete(self):
        self.results = self.recorder.get_upload_record()
        debug(self.results)
        if len(self.results['upload_record']) < self.blocknum:
            return 0
        for result in self.results['upload_record']:
            result = eval(result)
            if result['code'] != 200:
                return 0
        return 1

    def _is_complete_smart(self,result_list):
        '''
        :param result_list: 块上传的结果集合
        :return:
        '''
        if len(result_list) < self.blocknum:
            return 0
        for result in result_list:
            if result[0] != 200:
                return 0
        return 1

    def _get_failoffsets(self):
        offsetlist = [i *  int(self.block_size) for i in range(0, self.blocknum)]
        if self.results:
            for result in self.results['upload_record']:
                result = eval(result)
                if result['offset'] in offsetlist:
                    offsetlist.remove(result['offset'])
        return offsetlist
        
    def _get_blkstatus(self):
        blkstatus = []
        for offset in [i * (self.block_size) for i in range(0,self.blocknum)]:
            for result in self.results['upload_record']:
                result = eval(result)
                if offset == result['offset']:
                    blkstatus.append(result['ctx'])
        return blkstatus

    def _make_file(self,ctx_string):
        try:
            mkfile_retries = int(self.cfg.mkfile_retries)
        except ValueError as e:
            warning(u"parameter mkfile_retries is invalid, so use default value 3")
            mkfile_retries = 3
        url = https_check(self.__file_url())
        body = ctx_string #','.join(blkstatus)
        headers = self.__generate_headers()
        code,text,logid = _post(url=url,headers=headers,data=body)
        while mkfile_retries and self.__need_retry(code):
            debug('make file fail.retry upload')
            code,text,logid = _post(url=url,headers=headers,data=body)
            mkfile_retries -= 1
        return code,text,logid

    def _initial_records(self):
        self.uploadBatch = GetUuid()
        debug('New upload id: %s' % self.uploadBatch)

    def simple_multiupload(self,path,token):
        ctx_string = ''
        self._define_config(path,token)
        debug("Now start a new multipart upload task")
        self._initial_records()
        offsets = [i * (self.block_size) for i in range(0,self.blocknum)]
        if len(offsets) != 0:
            debug('There are %d offsets need to upload' % (len(offsets)))
            debug('Now start upload file blocks')
            if self.concurrency > 0:
                with ThreadPool(self.concurrency) as pool:
                    result_list = pool.map(self._make_block, offsets)
                for index,result_keys in enumerate(result_list):
                    blkcode,result,size = result_keys
                    if int(blkcode) != 200:
                        debug('Failed to upload the data of serial number {0}. Reason for failure:{1}'.format(index,result[2]))
                        raise WcsSeriveError("Multipart upload fail,please upload file again.Reason for failure:{0}".format(result[2]))
                    ctx_string += '{0},'.format(result[2])
                ctx_string = ctx_string.strip(',')
            elif self.concurrency == 0:
                for offset in offsets:
                    return_code ,result,size= self._make_block(offset)
                    if 400 <= int(return_code) <= 499:
                        debug('Single-Thread,attempt authentication failed,exit the task.')
                        sys.exit()
            else:
                raise ValueError('Invalid concurrency')
        debug('Now all blocks have upload suc.')
        mkfile_result = self._make_file(ctx_string)
        if 200 <= int(mkfile_result[0]) < 400:
            return mkfile_result
        else:
            raise WcsSeriveError("Make file fail,please upload file again.")
