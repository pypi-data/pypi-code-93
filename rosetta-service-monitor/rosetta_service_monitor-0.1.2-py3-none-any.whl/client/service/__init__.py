#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: xl
@file: __init__.py.py 
@time: 2021/08/09
@contact: 
@site:  
@software: PyCharm 
"""
import abc

from rosetta_service_monitor.client.enums import WarnningType


class MQBaseService(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def send_mq(self, project_name: str, err_msg: str, trace_id: str, request: dict,
                      warnning_type: WarnningType = WarnningType.normal, **kwargs):
        pass

    def close(self):
        ...


class MQNoUseService(MQBaseService):

    async def send_mq(self, project_name: str, err_msg: str, trace_id: str, request: dict,
                      warnning_type: WarnningType = WarnningType.normal, **kwargs):
        return ""
