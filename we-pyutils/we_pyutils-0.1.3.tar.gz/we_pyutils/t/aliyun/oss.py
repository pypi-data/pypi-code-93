#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : oss.py
@Time    : 2020-02-09 8:23
@Author  : ZENKR
@Email   : zenkr@qq.com
@Software: PyCharm
@Desc    :
@license : Copyright (c) 2020 WingEase Technology Co.,Ltd. All Rights Reserved.
"""
import os

import oss2

DEFAULT_ENDPOINT = os.getenv('ALIYUN_OSS_ENDPOINT', '')
DEFAULT_ACCESS_KEY_ID = os.getenv('ALIYUN_OSS_ACCESS_KEY_ID', '')
DEFAULT_ACCESS_KEY_SECRET = os.getenv('ALIYUN_OSS_ACCESS_KEY_SECRET', '')
DEFAULT_BUCKET_NAME = os.getenv('ALIYUN_OSS_BUCKET_NAME', '')


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance


class AliyunOssClient(Singleton):
    buckets = {}
    bucket_name = None

    def __init__(self, endpoint=None, key_id=None, key_secret=None):
        self.endpoint = endpoint if endpoint else DEFAULT_ENDPOINT
        self.key_id = key_id if key_id else DEFAULT_ACCESS_KEY_ID
        self.key_secret = key_secret if key_secret else DEFAULT_ACCESS_KEY_SECRET

    def get_oss_bucket(self, bucket_name=None):
        if bucket_name:
            self.bucket_name = bucket_name
        elif self.bucket_name:
            pass
        else:
            self.bucket_name = DEFAULT_BUCKET_NAME
        if bucket_name not in self.buckets:
            auth = oss2.Auth(self.key_id, self.key_secret)
            self.buckets[bucket_name] = oss2.Bucket(auth, self.endpoint, self.bucket_name)
        return self.buckets[bucket_name]


if __name__ == '__main__':
    import environ
    from we_pyutils.env import GetEnv

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROJECT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
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
    end_point = env.str('ALIYUN_OSS_ENDPOINT', '')
    key = env.str('ALIYUN_OSS_ACCESS_KEY_ID', '')
    secret = env.str('ALIYUN_OSS_ACCESS_KEY_SECRET', '')
    bucket_name = env.str('ALIYUN_OSS_BUCKET_NAME', '')
    client = AliyunOssClient(end_point, key, secret)
    bucket = client.get_oss_bucket(bucket_name)
    pass
