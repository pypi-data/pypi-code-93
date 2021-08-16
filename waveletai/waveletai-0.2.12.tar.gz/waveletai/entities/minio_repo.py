#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2020/6/30 9:39
@Author  : WaveletAI-Product-Team Janus
@license : (C) Copyright 2019-2022, Visionet(Tianjin)Information Technology Co.,Ltd.
@Site    : plus.xiaobodata.com
@File    : MinioRepo.py
@Desc    : 
"""

from waveletai.entities._base_object import _BaseObject
from waveletai.entities.minio_bucket import MinioBucket
import re


class MinIORepo(_BaseObject):
    def __init__(self, host, buckets=None, access_key=None, secret_key=None, secure=False):
        self._host = host
        self._buckets = buckets
        self._access_key = access_key
        self._secret_key = secret_key
        self._secure = secure

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, host):
        """
        minio主机
        :param value:
        :return:
        """
        self._host = host

    @property
    def access_key(self):
        return self._access_key

    @access_key.setter
    def access_key(self, access_key):
        """
        minio用户名
        :param value:
        :return:
        """
        self._access_key = access_key

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, secret_key):
        """
        minio密码/token令牌
        :param value:
        :return:
        """
        self._secret_key = secret_key

    @property
    def secure(self):
        """
        将此值设置为"True"以启用安全（HTTPS）访问。
        :return:
        """
        return self._secure

    @secure.setter
    def secure(self, secure):
        self._secure = secure

    @property
    def buckets(self):
        return self._buckets

    @buckets.setter
    def buckets(self, bucket):
        """
        追加Minio bucket到默认系统主题的列表中
        :param bucket:
        :return:
        """
        if isinstance(bucket, MinioBucket):
            self._buckets.append(bucket)
        else:
            raise TypeError("bucket require <MinioBucket> class type as input")

    def search_buckets(self, module=None, bucketName=None, objectPath=None):
        """
        Get a list of <MinioBucket> fit the search criteria.
        :param module: 模块名称,精确匹配
        :param bucketName: 桶名称,精确匹配
        :param objectPath: 对象路径 完整表达式,正则匹配
        :return:
        """
        buckets = []
        for bucket in self.buckets:
            if bucketName:
                if bucketName == bucket.bucketName:
                    buckets.append(bucket)
                    continue
            if objectPath:
                if re.search(objectPath, bucket.objectPath):
                    buckets.append(bucket)
                    continue
            if module:
                if module == bucket.module:
                    buckets.append(bucket)
                    continue
        return buckets
