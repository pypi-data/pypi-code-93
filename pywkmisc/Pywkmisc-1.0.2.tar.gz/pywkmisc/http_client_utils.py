#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import logging.config
from contextlib import closing
from pywkmisc import DateUtils
from .mimetype_utils import MimeTypeUtils
'''
Created on 2020年7月22日

@author: wangkai

定义一些系统变量
'''

logger = logging.getLogger('httpclient')


class HttpClientUtils(object):
    SYSTEM_VERSION = "spider-sdk-python-VersionNo"

    @staticmethod
    def get(url,
            params={},
            headers={'cache-control': "no-cache"},
            method='GET',
            payload=None,
            verify=True,
            proxies=True):
        """
        获取网络对象
        :param url:						网址
        :param params:				参数
        :param headers:				头部信息
        :param method:				请求类型 GET POST PUT
        :param payload:				请求data数据
        :param verify:				证书代理
        :return:							网络请求信息
        """
        logger.info(url)
        if proxies is True:
            return requests.request(method,
                                    url,
                                    data=payload,
                                    headers=headers,
                                    params=params,
                                    timeout=100,
                                    verify=verify)
        else:
            return requests.request(method,
                                    url,
                                    data=payload,
                                    headers=headers,
                                    params=params,
                                    timeout=100,
                                    verify=verify)

    @staticmethod
    def getjson(url,
                params={},
                headers={'cache-control': "no-cache"},
                method='GET',
                payload=None,
                verify=True,
                proxies=None):
        """
        网络对象转为文本
        :param url: 网址
        :param params: 参数
        :param headers: 头部信息
        :param method: 请求类型 GET POST PUT
        :param payload: 请求data数据
        :param verify: 证书代理
        :param proxies: 是否使用代理服务器
        :return: JSON数据
        """
        response = HttpClientUtils.get(url, params, headers, method, payload, verify, proxies)
        return json.loads(response.text)

    @staticmethod
    def _get_ext(qheader,default_ext = None):
        if default_ext:
            return default_ext
        ext = MimeTypeUtils().get_content_type_ext(
            MimeTypeUtils().get_content_type(qheader.headers))
        return ext

    @staticmethod
    def save_file(url,
                  savepath,
                  params={},
                  headers={'cache-control': "no-cache"},
                  method='GET',
                  save_file_name=None,
                  ext=None,
                  payload=None,
                  verify=True):
        qheader = HttpClientUtils.request_head(url)

        # todo 获取不到文件的大小的问题
        content_length = 0
        if 'Content-Length' in qheader:
            content_length = qheader.headers['Content-Length'] | 0
        _file_size = HttpClientUtils.size_format(content_length)
        ext = HttpClientUtils._get_ext(qheader, ext)
        if save_file_name is None:
            save_file_name = str(DateUtils.get_timestamp())
        save_file_name = "{}{}{}".format(savepath, save_file_name, ext)
        i = 0
        with closing(requests.request(method,
                                      url,
                                      data=payload,
                                      headers=headers,
                                      params=params,
                                      timeout=100,
                                      verify=verify,
                                      stream=True)) as res:
            old_bfb = ''

            if content_length == 0:
                logger.debug('获取不到文件大小')
            else:
                logger.debug('{}(size:{})->{}'.format(url, _file_size, save_file_name))
            with open(save_file_name, "wb") as f:
                for chunk in res.iter_content(chunk_size=1024):
                    if chunk:
                        i += len(chunk)
                        f.write(chunk)
                        if content_length >0:
                            bfb = '{:.0%}'.format(i/int(content_length))
                            if bfb != old_bfb:
                                old_bfb = bfb
                                print('\r{bfb}({chunk}/{total}),'.format(bfb=bfb, chunk=HttpClientUtils.size_format(i), total=_file_size), end="")
                        else:
                            print('\r{chunk},'.format(chunk=HttpClientUtils.size_format(i)), end="")
            print('')
        return save_file_name

    @staticmethod
    def size_format(size, is_disk=False, precision=2):
        formats = ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        unit = 1000.0 if is_disk else 1024.0
        if isinstance(size, str):
            size = int(size)
        if not(isinstance(size, float) or isinstance(size, int)):
            raise TypeError('a float number or an integer number is required!')
        if size < 0:
            raise ValueError('number must be non-negative')
        for i in formats:
            size /= unit
            if size < unit:
                return f'{round(size, precision)}{i}'
        return f'{round(size, precision)}{i}'

    @staticmethod
    def request_head(url, headers={'cache-control': "no-cache"}):
        response = requests.head(url, headers=headers)
        if 'Location' in response.headers:
            if url != response.headers['Location']:
                return HttpClientUtils.request_head(response.headers['Location'])
        return response


if __name__ == '__main__':
    pass
