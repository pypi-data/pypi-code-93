#coding:utf-8
'''
Created on 2016-9-1

@author: xzregg
'''

import requests
import urllib.request, urllib.parse, urllib.error,urllib.request,urllib.error,urllib.parse
import hashlib
import datetime
import urllib.parse

def md5(_str):
    return hashlib.new('md5',_str).hexdigest()

class UpYUN(object):
    
    PURGE_API = 'http://purge.upyun.com/purge/';
    REST_API = 'http://v0.api.upyun.com'
    
    GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    def __init__(self,bucketname='i9133-download-cdn', username='apk9133cdn', password='@ouJ@OI#1'):
        self.bucketname = bucketname
        self.username = username
        self.password = md5(password)
        self.urls = ''
        
    def purge_req(self):
        date = datetime.datetime.utcnow().strftime(self.GMT_FORMAT)
        
        sign_str = '%s&%s&%s&%s' % (self.urls,self.bucketname,date,self.password)
        
        sign = md5(sign_str)
        
        authorization = ' UpYun %s:%s:%s' % (self.bucketname,self.username,sign)
        
        headers = {'Content-Type':'application/x-www-form-urlencoded',
                   'Authorization': authorization,
                   'Date' : date,
                   }

        data = {"purge":self.urls}
        post_data = urllib.parse.urlencode(data)

        r = requests.post(self.PURGE_API, data=post_data, headers=headers)

        return r.status_code ,r.json()
        
    def delelte_mirror_path(self,path):
        '''删除镜像文件
        '''
        date = datetime.datetime.utcnow().strftime(self.GMT_FORMAT)
        content_length = 0
        path = urllib.parse.urlparse(path).path
        bucket = '/%s%s' % (self.bucketname,path)
        
        sign_str = 'DELETE&%s&%s&%s&%s' % (bucket,date,content_length,self.password)
        
        sign = md5(sign_str)
        
        authorization = ' UpYun %s:%s' % (self.username,sign)
        
        headers = {'Content-Type':'application/x-www-form-urlencoded',
                   'Authorization': authorization,
                   'Date' : date,
                   'Content-Length': 0,
                   'x-upyun-async' :' ture'
                   }

        req_url = urllib.parse.urljoin(self.REST_API,bucket)

        r = requests.delete(req_url, headers=headers)
        print(r.text,r.status_code)
        return r.status_code 
    
        
    def refresh_cdn_cache(self,*urls):
        for path in urls:
            self.delelte_mirror_path(path)
        self.urls = '%s\n' % '\n'.join(urls)
        result = self.purge_req()
        print(result)
        return result
    
    
if __name__ == '__main__':
    upyun = UpYUN()
    #print upyun.delelte_mirror_path('/apk/test1.txt')
    upyun.refresh_cdn_cache('http://download.9133.com/apk/fytx_test/fytx_test_i9133_i9133_i9133001.apk',
                            'http://download.9133.com/apk/test.txt',
                            )

    
    