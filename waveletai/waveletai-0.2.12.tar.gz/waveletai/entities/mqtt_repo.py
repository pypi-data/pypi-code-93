#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2020/6/30 9:39
@Author  : WaveletAI-Product-Team Janus
@license : (C) Copyright 2019-2022, Visionet(Tianjin)Information Technology Co.,Ltd.
@Site    : plus.xiaobodata.com
@File    : MqttRepo.py
@Desc    : 
"""

from waveletai.entities._base_object import _BaseObject
from waveletai.entities.mqtt_topic import MqttTopic
import re


class MqttRepo(_BaseObject):
    def __init__(self, host, port, topics=None, username=None, password=None):
        self._host = host
        self._port = port
        self._topics = topics
        self._username = username
        self._password = password

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        """
        mqtt用户名
        :param value:
        :return:
        """
        self._username = username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        """
        mqtt密码/token令牌
        :param value:
        :return:
        """
        self._password = password

    @property
    def topics(self):
        return self._topics

    @topics.setter
    def topics(self, topic):
        """
        追加MQTT topic到默认系统主题的列表中
        :param topic:
        :return:
        """
        if isinstance(topic, MqttTopic):
            self._topics.append(topic)
        else:
            raise TypeError("topics require <MqttTopic> class type as input")

    def search_topics(self, module=None, topicFilter=None, topicExpression=None):
        """
        Get a list of <MqttTopic> fit the search criteria.
        :param module: topic 模块名称,精确匹配
        :param topicFilter: topic 正则表达式,正则匹配
        :param topicExpression: topic 完整表达式,精确匹配
        :return:
        """
        topics = []
        for topic in self.topics:
            if topicExpression:
                if topicExpression == topic.topicExpression:
                    topics.append(topic)
                    continue
            if topicFilter:
                if re.search(topicFilter, topic.topicFilter):
                    topics.append(topic)
                    continue
            if module:
                if module == topic.module:
                    topics.append(topic)
                    continue
        return topics
