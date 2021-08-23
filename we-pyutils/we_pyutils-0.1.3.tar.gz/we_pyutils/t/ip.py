#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : ip.py
@Time    : 2020-02-09 8:59
@Author  : ZENKR
@Email   : zenkr@qq.com
@Software: PyCharm
@Desc    :
@license : Copyright (c) 2020 WingEase Technology Co.,Ltd. All Rights Reserved.
"""
import json
import os

import requests

DEFAULT_GET_MY_IP_URL = os.getenv('DEFAULT_GET_MY_IP_URL', 'https://www.zenkr.com/tools/getip')


def get_my_ip(url=DEFAULT_GET_MY_IP_URL, tries=3, count=1):
    """
    获取当前IP地址
    :param tries: 尝试次数
    :param count: 当前次数
    :return: IP 或 None
    """
    print(f'Try to get my IP.')
    if count <= tries:
        try:
            req = requests.get(url)
            content = str(req.content, encoding='utf-8')
            my_ip = json.loads(content)['ip']
            return my_ip
        except Exception as e:
            print(f'Can not get my IP. detail: {e}')
            return get_my_ip(tries=tries, count=count + 1)
    return None


if __name__ == '__main__':
    import environ
    from we_pyutils.env import GetEnv

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROJECT_DIR = os.path.dirname(BASE_DIR)
    HOME_DIR = os.path.expanduser('~')
    dir_list = [
        BASE_DIR,
        PROJECT_DIR,
        HOME_DIR,
    ]

    e = GetEnv(dir_list)
    env_path = e.get_env()
    env = environ.Env()
    if env_path:
        env.read_env(env_path)
    url = env.str('GET_MY_IP_URL', '')
    pass
