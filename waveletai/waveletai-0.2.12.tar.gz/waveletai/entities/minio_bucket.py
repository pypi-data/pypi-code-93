#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2020/6/30 10:02
@Author  : WaveletAI-Product-Team Janus
@license : (C) Copyright 2019-2022, Visionet(Tianjin)Information Technology Co.,Ltd.
@Site    : plus.xiaobodata.com
@File    : BucketRepo.py
@Desc    : 
"""
from waveletai.entities._base_object import _BaseObject


class MinioBucket(_BaseObject):
    def __init__(self, module, bucketName, objectPath):
        self._module = module
        self._bucketName = bucketName
        self._objectPath = objectPath

    @property
    def module(self):
        return self._module

    @property
    def bucketName(self):
        return self._bucketName

    @property
    def objectPath(self):
        return self._objectPath
