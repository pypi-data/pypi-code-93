# -*- coding: utf-8 -*-
# @Time    : 2021-03-24 16:51
# @Author  : xzr
# @File    : consumers
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : https://channels.readthedocs.io/en/stable/topics/routing.html#channelnamerouter

import logging
import time

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework.exceptions import ValidationError

from framework.utils import json_dumps, trace_msg

logger = logging.getLogger('uvicorn.access')

from .serializer import ModelEventDataSer, ModelEventActions, DEFAULT_ALL_GROUP_NAME, EventDataSer
from django.apps import apps


class WebsocketGateWayConsumer(AsyncJsonWebsocketConsumer):
    join_groups = set()
    req_id = 0
    allow_groups_map = dict([(m.get_table_name(), m) for m in apps.get_models() if hasattr(m, 'get_table_name')])

    @property
    def clinet_name(self):
        return '%s %s' % (str(self.scope['client']), self.channel_name)

    async def join_to_group(self, group_name):
        logger.info('%s join %s' % (self.clinet_name, group_name))
        self.join_groups.add(group_name)
        await self.channel_layer.group_add(group_name, self.channel_name)

    async def leave_groups(self):
        for group_name in self.join_groups:
            await self.channel_layer.group_discard(group_name, self.channel_name)

    async def connect(self):
        user = self.scope['user']
        if user.is_authenticated:
            logger.info('%s connect' % self.clinet_name)
            await self.join_to_group(DEFAULT_ALL_GROUP_NAME)
            await self.accept()
        else:
            logger.info('%s not authenticated' % self.clinet_name)
            await self.close()

    async def disconnect(self, close_code):
        await self.leave_groups()

    async def receive_json(self, event: EventDataSer, **kwargs):
        self.req_id += 1
        rsp_event_data = EventDataSer()
        try:
            req_event_data = EventDataSer(event)
            if req_event_data.o.action == ModelEventActions.SUBSCRIBE:
                req_event_data = ModelEventDataSer(event)
                for model_name in req_event_data.o.model.split(','):
                    if model_name and self.allow_groups_map.get(model_name, None):
                        await self.join_to_group(req_event_data.o.model)
            rsp_event_data.o.update(req_event_data.initial_data)
        except ValidationError as e:
            rsp_event_data.o.code = 1
            rsp_event_data.o.data = e.detail
            rsp_event_data.o.msg = e.default_code
        except Exception as e:
            logger.error(trace_msg())
            rsp_event_data.o.code = 1
            rsp_event_data.o.msg = str(e.args[0])

        rsp_event_data.o.req_id = rsp_event_data.o.req_id or self.req_id
        await self.send_json(rsp_event_data)

    async def model_signal(self, event_data: ModelEventDataSer):
        """django 模型信号响应"""
        await self.send_json(ModelEventDataSer(event_data))

    async def system_message(self, event_data):
        """系统消息"""
        await self.send_json(EventDataSer(event_data))

    async def send_json(self, event_data: EventDataSer, close=False):
        event_data.o.server_time = int(time.time() * 1000)
        event_data.o.channel_name = self.channel_name
        await super().send(text_data=json_dumps(event_data.data), close=close)
