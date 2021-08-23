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
import os
import socket
import time

from loguru import logger

from rosetta_service_monitor.client.enums import WarnningType
from rosetta_service_monitor.tasks.baskground_task_actor import BackgroundWorker


class MQBaseService(metaclass=abc.ABCMeta):
    def __init__(self):
        self._worker = BackgroundWorker()

    @abc.abstractmethod
    async def send_mq(self, project_name: str, err_msg: str, trace_id: str, request: dict,
                      warnning_type: WarnningType = WarnningType.normal, **kwargs):
        pass

    def async_run(self, func, *args, **kwargs):
        f = self._worker.submit(func, *args, **kwargs)
        return f

    def close(self):
        ...


class MQNoUseService(MQBaseService):
    def __init__(self):
        super(MQNoUseService, self).__init__()

    async def send_mq(self, project_name: str, err_msg: str, trace_id: str, request: dict,
                      warnning_type: WarnningType = WarnningType.normal, **kwargs):
        hostname = socket.gethostname()
        time.sleep(5)
        host_info = {
            'hostname': hostname,
            'ip': os.getenv("HOST_IP"),
            'pod_name': os.getenv("MY_POD_NAME"),
            'pod_ip': os.getenv("POD_IP")
        }

        msg = {
            'project_name': project_name,
            'trace_id': trace_id,
            'reason': err_msg,
            'request': request,
            'hostinfo': host_info,
            'stage': warnning_type.value
        }
        msg.update(kwargs)
        logger.info(f"send msg: {msg}")
        return ""

    def send_msg_async(self, project_name: str, err_msg: str, trace_id: str, request: dict,
                       warnning_type: WarnningType = WarnningType.normal, **kwargs):
        r = self.async_run(self.send_mq, project_name, err_msg, trace_id, request,
                           warnning_type, **kwargs)
        return r