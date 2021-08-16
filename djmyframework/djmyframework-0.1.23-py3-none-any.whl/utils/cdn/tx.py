#!/usr/bin/env python
#coding:utf-8
import os
import hashlib
import urllib.request, urllib.parse, urllib.error
import requests
import binascii
import hmac
import copy
import random
import sys
import time,datetime
from pprint import pprint
from optparse import OptionParser
#from requests.packages.urllib3.exceptions import InsecurePlatformWarning
#requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
#from requests.packages.urllib3.exceptions import InsecureRequestWarning
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try: import simplejson as json
except: import json

class Sign:
    def __init__(self, secretId, secretKey):
        self.secretId = secretId
        self.secretKey = secretKey

    def make(self, requestHost, requestUri, params, method = 'GET'):
        srcStr = method.upper() + requestHost + requestUri + '?' + "&".join(k.replace("_",".") + "=" + str(params[k]) for k in sorted(params.keys()))
        hashed = hmac.new(self.secretKey, srcStr, hashlib.sha1)
        return binascii.b2a_base64(hashed.digest())[:-1]

class Request:
    timeout = 10
    version = 'Python_Tools'
    def __init__(self, secretId, secretKey):
        self.secretId = secretId
        self.secretKey = secretKey

    def send(self, requestHost, requestUri, params, files = {}, method = 'GET', debug = 0):
        params['RequestClient'] = Request.version
        params['SecretId'] = self.secretId
        sign = Sign(self.secretId, self.secretKey)
        params['Signature'] = sign.make(requestHost, requestUri, params, method)

        url = 'https://%s%s' % (requestHost, requestUri)

        if debug:
            print(method.upper(), url)
            print('Request Args:')
            pprint(params)
        if method.upper() == 'GET':
            req = requests.get(url, params=params, timeout=Request.timeout,verify=False)
        else:
            req = requests.post(url, data=params, files=files, timeout=Request.timeout,verify=False)

        if debug:
            print("Response:", req.status_code, req.text)
        if req.status_code != requests.codes.ok:
            req.raise_for_status()

        rsp = {}
        try:
            rsp = json.loads(req.text)
        except:
            raise ValueError("Error: response is not json\n%s" % req.text)

        code = rsp.get("code", -1)
        message = rsp.get("message", req.text)
        if rsp.get('code', -404) != 0:
            raise ValueError("Error: code=%s, message=%s" % (code, message))
        if rsp.get('data', None) is None:
            return req.status_code,'request is success.'
        else:
            return req.status_code,rsp['data']
            
            
class TxQcloudQpi(object):
        host = 'cdn.api.qcloud.com'
        uri = '/v2/index.php'
        method = "POST"
        secret_id='AKIDSq7IKC2UzQlwwmh3Wq6DAxa4Peq4o61n'
        secret_key='mPsCMlDar23tZ5ThlfQ1Z1KUcfYP7i9Q'
        #星玩,AKIDSq7IKC2UzQlwwmh3Wq6DAxa4Peq4o61n mPsCMlDar23tZ5ThlfQ1Z1KUcfYP7i9Q

        def __init__(self,secret_id='AKIDAFJE5p9xISQHwQDroaJvMzlOq6B6aR3b',secret_key='azFLG0a6VjngPyMaeXHtLfp5IKCuVvAE',debug=1):
            self.secret_id = secret_id
            self.secret_key = secret_key
            self.debug = debug
            
        def _make_params(self):
            self.params = {
                'Region': 'gz',
                'Nonce': random.randint(1, sys.maxsize),
                'Timestamp': int(time.time()),
                }
            
        def refreshCdnUrl(self,urls):
            self.files = {}
            self._make_params()
            self.params['Action']  = 'RefreshCdnUrl'

            for idx,val in enumerate(urls) :
                self.params["%s.%s"%('urls', idx)] = val
            request = Request(self.secret_id, self.secret_key)
            try:
                r = request.send(self.host, self.uri, self.params, self.files, self.method, self.debug)
            except Exception as e:
                r = str(e)
            return r

        def pushCdnUrl(self,urls):
            """预热cdn"""
            self.files = {}
            self._make_params()
            self.params['Action']  = 'CdnPusherV2'

            for idx,val in enumerate(urls) :
                self.params["%s.%s"%('urls', idx)] = val
            request = Request(self.secret_id, self.secret_key)
            try:
                r = request.send(self.host, self.uri, self.params, self.files, self.method, self.debug)
            except Exception as e:
                r = str(e)
            return r


        def refreshCdnDir(self,dirs):
            self.files = {}
            self._make_params()
            self.params['Action']  = 'RefreshCdnDir'

            for idx,val in enumerate(dirs) :
                self.params["%s.%s"%('dirs', idx)] = val
            request = Request(self.secret_id, self.secret_key)
            try:
                r = request.send(self.host, self.uri, self.params, self.files, self.method, self.debug)
            except Exception as e:
                r = str(e)
            return r
        
        def GetCdnStatTop(self,projects_id='1033998',host='download.9133.com',sdate='',edate='',statType='flux'):
            self.files = {}
            self._make_params()
            self.params['Action']  = 'GetCdnStatTop'

            self.params['projects.0']=projects_id
            self.params['startDate'] = sdate or datetime.datetime.now().strftime('%Y%m%d')
            self.params['endDate'] = edate or datetime.datetime.now().strftime('%Y%m%d')
            self.params['statType'] = statType #排名依据，共有三种类型，其中 'flux' 代表累计流量，单位Byte；'bandwidth' 代表峰值带宽，单位bps；'requests' 代表请求数，单位次；
            self.params['hosts.0'] = host

            request = Request(self.secret_id, self.secret_key)
            try:
                r = request.send(self.host, self.uri, self.params, self.files, self.method, self.debug)
            except Exception as e:
                r = str(e)
            return r
            
if __name__ == '__main__':
    #print TxQcloudQpi().refreshCdnUrl(['http://download.uuufish.com/index.html','https://cdn.uuufish.com/static/skin/metro/font/IcoMoon.woff'])
    print(TxQcloudQpi().GetCdnStatTop())
    