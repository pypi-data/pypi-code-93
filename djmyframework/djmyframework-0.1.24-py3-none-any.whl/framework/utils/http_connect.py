# -*- coding: utf-8 -*-
# @Time    : 2020-07-13 15:48
# @Author  : xzr
# @File    : http_connect
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

import requests


def http_post(url, data='', data_type='x-www-form-urlencoded', user_agent='', timeout_param=5, timeout=5, headers=[],
              cookie=''):
    if data:
        rsp = requests.post(url, data=data, timeout=timeout or timeout_param)
    else:
        rsp = requests.get(url, timeout=timeout or timeout_param)
    return rsp.content
