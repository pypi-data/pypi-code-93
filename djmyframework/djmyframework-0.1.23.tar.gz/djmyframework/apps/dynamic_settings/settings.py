# -*- coding: utf-8 -*-




import os

from  datetime import datetime
from .conf import SettingOptions

# etcd3.client parmas
_SETTINGS_LOADER_ETCD = dict(host='localhost', port=2379,
                            ca_cert=None, cert_key=None, cert_cert=None, timeout=None,
                            user=None, password=None, grpc_options=None, prefix_key=os.environ.get('DJANGO_ENV', 'dev'))

# redis.StrictRedis.from_url parmas
_SETTINGS_LOADER_REDIS = dict(url='redis://:123456@10.19.200.185:6379/5', decode_responses=True,
                             prefix_key=os.environ.get('DJANGO_ENV', 'dev'))




TEST_LIST_SETTINGS = SettingOptions([1,2,3,4],'测试列表','TEST_LIST_SETTINGS','test')

TEST_DICT_SETTINGS = SettingOptions({"k1":"v1","k2":"v2","k3":"v3"},'测试字典','TEST_DICT_SETTINGS','test')

TEST_FLOAT_SETTINGS = SettingOptions(1.1,'测试浮点','TEST_FLOAT_SETTINGS','test')
TEST_DTETIME_SETTINGS = SettingOptions('2011-11-04 00:05:23','测试时间','TEST_DTETIME_SETTINGS','test')

# 全局配置覆盖项目
from settings import *