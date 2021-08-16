# -*- coding: utf-8 -*-
# @Author: wei.fu
# @Date:   2021-07-20 14:22:36
# @Last Modified by:   wei.fu
# @Last Modified time: 2021-07-22 14:16:01
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# here put the import lib

import requests
from loguru import logger
import urllib
import ssl
import json

import queue


class JSONUnmarshalError(Exception):
    def __init__(self, msg=None):
        self.msg = msg


class ServerUnknownError(Exception):
    def __init__(self,
                 code=500,
                 message="server unknown error",
                 title="Server Error",
                 error=object):
        self.code = code
        self.message = message
        self.detail = str(error)


def http_request(url, method='POST', data={}, headers={}, cookies={}):
    """
    通用请求方法

    :param url:
    :param data: post data
    :param params: get data
    :param headers: request headers
    """
    try:
        method = method.upper()
        r = requests.request(method,
                             url,
                             data=data,
                             headers=headers,
                             cookies=cookies)

    except Exception as e:
        raise e

    try:
        return r.json()

    except Exception as e:
        raise JSONUnmarshalError('JSON解析出错, 信息: {0}'.format(str(e)))


class KrakenAuthMain:
    def __init__(self, auth_domain, access_key, access_sceret):
        ssl._create_default_https_context = ssl._create_unverified_context
        self._token_domain = auth_domain
        self._access_key = access_key
        self._access_secret = access_sceret
        self.token = self._get_token()

    def _get_token(self):
        data = b'{"access_key": "%s", "access_secret": "%s"}'  \
            % (bytes(self._access_key,  encoding='utf-8'), bytes(self._access_secret, encoding='utf-8'))
        try:
            headersMap = {
                "Content-Type": "application/json",
            }
            url = self._token_domain + '/api/auth/v1/tokens/'
            req = urllib.request.Request(url=url,
                                         headers=headersMap,
                                         data=data,
                                         method='POST')
            response = urllib.request.urlopen(req)
            if response.status == 200:
                data = response.read()
                result = json.loads(data)
                return result['data']["token"]
            else:
                msg = '请求认证服务器异常:status code %s' % response.status
                logger.error(msg)
                raise ServerUnknownError(message=msg)

        except Exception as e:
            msg = "获取token 异常" + str(e)
            logger.error(msg)
            raise ServerUnknownError(message=msg)

    def get_projects(self):
        project_url = self._token_domain + '/api/auth/v1/project_manager/'
        headers = {'Authorization': 'Basic ' + self.token}
        request_json = http_request(project_url, method='get', headers=headers)
        # logger.debug(request_json)
        return request_json

    def get_cost_center(self):
        url = self._token_domain + '/api/auth/v1/cost_center/'
        headers = {'Authorization': 'Basic ' + self.token}
        req_data = http_request(url, method='get', headers=headers)
        return req_data

    def get_user_competence(self, account_name):
        """  获取用户权限信息 """
        url = self._token_domain + \
            '/api/auth/v1/user_competence/?account_name=' + account_name
        headers = {'Authorization': 'Basic ' + self.token}
        req_data = http_request(url, method='get', headers=headers)
        return req_data

    def get_const_center_map(self):
        req = self.get_cost_center()
        result = dict()
        if req['code'] == 20000:
            data_list = req['data']
            q = queue.Queue()
            q.put(data_list)
            while not q.empty():
                datas = q.get()
                for i in datas:
                    cost_center_name = i.get('cost_center_name')
                    cost_center_code = i.get('cost_center_code')
                    children = i.get('children')
                    if cost_center_code:
                        result[cost_center_code] = cost_center_name
                    if children:
                        q.put(children)
        else:
            raise ServerUnknownError(message=req['message'])
        return result


if __name__ == '__main__':
    pass
