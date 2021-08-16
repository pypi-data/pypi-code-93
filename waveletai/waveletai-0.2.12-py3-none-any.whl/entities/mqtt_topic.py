#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2020/6/30 10:13
@Author  : WaveletAI-Product-Team Janus
@license : (C) Copyright 2019-2022, Visionet(Tianjin)Information Technology Co.,Ltd.
@Site    : plus.xiaobodata.com
@File    : topic_repo.py
@Desc    : 
"""
from waveletai.entities._base_object import _BaseObject


class MqttTopic(_BaseObject):
    def __init__(self, module, topicFilter, topicExpression, timeout=60000):
        self._module = module
        self._topicFilter = topicFilter
        self._topicExpression = topicExpression
        self._timeout = timeout

    @property
    def module(self):
        return self._module

    @property
    def topicFilter(self):
        return self._topicFilter

    @property
    def topicExpression(self):
        return self._topicExpression

    @property
    def timeout(self):
        return self._timeout
