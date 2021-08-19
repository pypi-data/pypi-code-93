#!/usr/bin/python
## -*- coding: utf-8 -*-
import os

from wcs.commons.util import urlsafe_base64_encode
from wcs.commons.auth import Auth
from wcs.services.simpleupload import SimpleUpload
from wcs.services.streamupload import StreamUpload
from wcs.services.multipartupload import MultipartUpload
from wcs.services.simple_multipartupload import Simple_MultipartUpload
from wcs.services.filemanager import BucketManager
from wcs.services.fmgr import Fmgr
from wcs.services.persistentfop import PersistentFop
from wcs.services.wslive import WsLive
from wcs.commons.putpolicy import PutPolicy
from wcs.commons.error_deal import WcsSeriveError

class Client(object):
    """接口封装类
    该类封装了SDK提供的全部API，用户在开发时只需要实例化这个类就可以调用SDK提供的全部接口，而不需要根据不同的API实例化不同的类
    Attributes:
        auth: 上传&管理token计算实例
        simpleupload: 普通上传实例
        streamupload: 流地址上传实例
        multiupload: 分片上传实例
        bmgr: 资源管理实例
        fmgr: 高级资源管理实例
        pfops: 音视频持久化操作实例
        wsl: 直播录制文件列举实例
        cfg: 配置文件管理实例
    """
    def __init__(self, config):
        self.auth = Auth(config.access_key, config.secret_key)
        self.cfg = config

    def simple_upload(self, path, bucket, key):
        simpleupload = SimpleUpload(self.cfg.put_url)
        policy = PutPolicy()
        policy.set_conf('scope', '%s:%s' % (bucket,key))
        policy.dump_policy(self.cfg)
        token = self.auth.uploadtoken(policy.putpolicy)
        return simpleupload.upload(path,token ,key)

    def stream_upload(self, stream, bucket, key):
        streamupload = StreamUpload(self.cfg.put_url)
        policy = PutPolicy()
        policy.set_conf('scope', '%s:%s' % (bucket,key))
        policy.dump_policy(self.cfg)
        token = self.auth.uploadtoken(policy.putpolicy)
        return streamupload.upload(stream,token ,key)

    def multipart_upload(self,path,bucket, key,tmp_upload_id=None):
        multiupload = MultipartUpload(self.cfg.put_url)
        policy = PutPolicy()
        policy.set_conf('scope', '%s:%s' % (bucket,key))
        policy.dump_policy(self.cfg)
        token = self.auth.uploadtoken(policy.putpolicy)
        upload_id = tmp_upload_id or self.cfg.upload_id
        return multiupload.upload(path,token,upload_id)

    def smart_upload(self,path,bucket, key,multi_size=20):
        simple_multiupload = Simple_MultipartUpload(self.cfg.put_url)
        simpleupload = SimpleUpload(self.cfg.put_url)
        policy = PutPolicy()
        policy.set_conf('scope', '%s:%s' % (bucket,key))
        policy.dump_policy(self.cfg)
        token = self.auth.uploadtoken(policy.putpolicy)
        file_size = 1024*1024*int(multi_size)
        if os.path.getsize(path) <= file_size:
            upload_result = simpleupload.upload(path ,token ,key)
            if 200 <= upload_result[0] <400:
                return upload_result
            else:
                raise WcsSeriveError('Upload file fail,erorr info:{0}'.format(upload_result))
        else:
            return simple_multiupload.simple_multiupload(path,token)

    def bucket_list(self,bucket,prefix=None, marker=None, limit=None, mode=None, starttime=None,endtime=None):
        bmgr = BucketManager(self.auth,self.cfg.mgr_url)
        try:
            pre = prefix or str(self.cfg.prefix)
        except Exception:
            pre = ''

        try:
            # m = mode or int(self.cfg.mode)
            if mode == None:
                m = int(self.cfg.mode)
            else:
                m = int(mode)
        except Exception:
            m = ''

        try:
            mar = marker or str(self.cfg.marker)
        except Exception:
            mar = ''
        try:
            l = limit or int(self.cfg.limit)
        except Exception:
            l = ''
        return bmgr.bucketlist(bucket,pre,mar,l,m, starttime, endtime)

    def bucket_listAll(self,bucket,prefix=None, marker=None, limit=None, mode=None, starttime=None,endtime=None):
        'List all files in the bucket.'
        bmgr = BucketManager(self.auth,self.cfg.mgr_url)
        _items = []
        try:
            pre = prefix or str(self.cfg.prefix)
        except Exception:
            pre = ''
        try:
            # m = mode or int(self.cfg.mode)
            if mode == None:
                m = int(self.cfg.mode)
            else:
                m = int(mode)
        except Exception:
            m = ''
        try:
            mar = marker or str(self.cfg.marker)
        except Exception:
            mar = ''
        try:
            l = limit or int(self.cfg.limit)
        except Exception:
            l = ''
        code, response, reqid = bmgr.bucketlist(bucket,pre,mar,l,m, starttime, endtime)
        if code == 200:
            _items += response.get('items')
            return_marker = response.get('marker')
            while return_marker:
                code, response, reqid = bmgr.bucketlist(bucket,pre,return_marker,l,m, starttime, endtime)
                if code != 200:
                    return code, response, reqid
                _items += response.get('items')
                return_marker = response.get('marker')
            response['items'] = _items
            return code,response,reqid
        else:
            return code, response, reqid

    def list_buckets(self):
        bmgr = BucketManager(self.auth,self.cfg.mgr_url)
        return bmgr.bucket_list()

    def bucket_stat(self, name, startdate, enddate,isListDetails='false',storageType=None):
        bmgr = BucketManager(self.auth,self.cfg.mgr_url)
        return bmgr.bucket_stat(name, startdate, enddate,isListDetails=isListDetails,storageType=storageType)

    def bucket_statistics(self, name, stype, startdate, enddate, isListDetails='false'):
        bmgr = BucketManager(self.auth,self.cfg.mgr_url)
        return bmgr.bucket_statistics(name, stype, startdate, enddate, isListDetails)

    def image_detect(self, image, dtype, bucket):
        bmgr = BucketManager(self.auth,self.cfg.mgr_url)
        return bmgr.image_detect(image, dtype, bucket)

    def stat(self,bucket,key):
        bmgr = BucketManager(self.auth,self.cfg.mgr_url)
        return bmgr.stat(bucket,key)

    def delete(self,bucket,key):
        bmgr = BucketManager(self.auth,self.cfg.mgr_url)
        return bmgr.delete(bucket,key)

    def move(self,srcbucket, srckey, dstbucket, dstkey=''):
        bmgr = BucketManager(self.auth,self.cfg.mgr_url)
        if dstkey:
            pass
        else:
            dstkey = srckey
        return bmgr.move(srcbucket, srckey, dstbucket, dstkey)

    def copy(self,srcbucket, srckey, dstbucket, dstkey=''):
        bmgr = BucketManager(self.auth,self.cfg.mgr_url)
        if dstkey:
            pass
        else:
            dstkey = srckey
        return bmgr.copy(srcbucket, srckey, dstbucket, dstkey)

    def setdeadline(self,bucket,key,deadline):
        bmgr = BucketManager(self.auth,self.cfg.mgr_url)
        return bmgr.setdeadline(bucket,key,deadline)

    def _parse_fops(self, fops):
        data = [fops]
        if self.cfg.notifyurl:
            data.append('notifyURL=%s' % urlsafe_base64_encode(self.cfg.notifyurl))
        if self.cfg.separate:
            data.append('separate=%s' % self.cfg.separate)
        if self.cfg.force:
            data.append('force=%s' % self.cfg.force)
        return 'fops=' + '&'.join(data)

    def fmgr_move(self, fops):
        fmgr = Fmgr(self.auth,self.cfg.mgr_url)
        return fmgr.fmgr_move(self._parse_fops(fops))

    def fmgr_copy(self, fops):
        fmgr = Fmgr(self.auth,self.cfg.mgr_url)
        return fmgr.fmgr_copy(self._parse_fops(fops))

    def fmgr_fetch(self, fops):
        fmgr = Fmgr(self.auth,self.cfg.mgr_url)
        return fmgr.fmgr_fetch(self._parse_fops(fops))

    def fmgr_delete(self, fops):
        fmgr = Fmgr(self.auth,self.cfg.mgr_url)
        return fmgr.fmgr_delete(self._parse_fops(fops))

    def prefix_delete(self, fops):
        fmgr = Fmgr(self.auth,self.cfg.mgr_url)
        return fmgr.prefix_delete(self._parse_fops(fops))

    def m3u8_delete(self, fops):
        fmgr = Fmgr(self.auth,self.cfg.mgr_url)
        return fmgr.m3u8_delete(self._parse_fops(fops))

    def fmgr_compress(self,fops):
        fmgr = Fmgr(self.auth,self.cfg.mgr_url)
        return fmgr.fmgr_compress(self._parse_fops(fops))

    def fmgr_status(self,persistentId):
        fmgr = Fmgr(self.auth,self.cfg.mgr_url)
        return fmgr.status(persistentId)

    def ops_execute(self,fops,bucket,key):
        pfops = PersistentFop(self.auth,self.cfg.mgr_url)
        f = int(self.cfg.force)
        if self.cfg.separate:
            separate = int(self.cfg.separate)
        else:
            separate = 0
        notifyurl = self.cfg.notifyurl or ''
        return pfops.execute(fops,bucket,key,f,separate,notifyurl)

    def ops_status(self,persistentId):
        pfops = PersistentFop(self.auth,self.cfg.mgr_url)
        return pfops.fops_status(persistentId)

    def wslive_list(self,channelname, startTime, endTime, bucket, start=None, limit=None):
        wsl = WsLive(self.auth,config.mgr_url)
        return wsl.wslive_list( channelname, startTime, endTime, bucket, start, limit)
