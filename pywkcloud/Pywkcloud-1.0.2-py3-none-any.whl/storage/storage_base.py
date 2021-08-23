#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pywkmisc import FileUtils, get_config


class StoreConfig(object):

    def __init__(self, config_name=None, config=None):
        if config_name:
            config = get_config(config_name)
        if not config:
            raise RuntimeError('''找不到参数，请配置参数，样例:
            {
                "accessKey": "",            #
                "secretKey": "",            #
                "bucketName": "",           # oss endpoint
                "endpoint": "",            # 连接的bucket地址
                "connectionTimeout": 120     # 连接超时时间，120秒为2分钟
                "defaultZone": ""           # 系统默认连接地址
            }''')

        self._access_key = config.get('accessKey')
        self._secret_key = config.get('secretKey')
        self._bucket_name = config.get('bucketName')
        self._endpoint = config.get('endpoint')
        self._connection_timeout = config.get('connectionTimeout', 120)
        self._default_zone = config.get('defaultZone')

    @property
    def access_key(self):
        return self._access_key

    @property
    def secret_key(self):
        return self._secret_key

    @property
    def bucket_name(self):
        return self._bucket_name

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def connection_timeout(self):
        return self._connection_timeout

    @property
    def default_zone(self):
        return self._default_zone


class StorageBase(object):
    
    def __init__(self, store_config: StoreConfig):
        self._store_config = store_config
        self._auth = None

    def get_auth(self):
        """
        获取凭证
        :return:
        """

    def check_bucket(self, key):
        """
        判断文件是否存在
        :param key:文件key
        :return True文件存在，False文件不存在
        """

    def upload_file(self, key, upload_file: FileUtils):
        """
        上传文件至oss
        :param key:         上传文件的key值
        :param upload_file:   文件路径
        :return:
        """

    def delete_file(self, key):
        """
        删除文件
        :param key:         上传文件的key值
        :return:
        """

    def get_file(self, key, filename: FileUtils):
        """
        下载一个文件到本地文件。
        :param key: 文件名
        :param filename: 本地文件名。要求父目录已经存在，且有写权限。
        :return: 如果文件不存在，则抛出 :class:`NoSuchKey <oss2.exceptions.NoSuchKey>` ；还可能抛出其他异常
        """
