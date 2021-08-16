# -*- coding: utf-8 -*-
# @Time    : 2019-09-09 15:42
# @Author  : xzr
# @File    : serializer
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :

from framework.response import DataSerializer, SUCCESS_CODE
from framework.serializer import s
from framework.translation import _
from framework.utils.myenum import Enum

DEFAULT_ALL_GROUP_NAME = 'default'


class EventActions(Enum):
    SUBSCRIBE = 'subscribe', _('订阅事件')


class EventDataSer(DataSerializer):
    code = s.IntegerField(label=_('返回Code'), default=SUCCESS_CODE, required=False)
    msg = s.CharField(label=_("业务消息"), default='ok')
    type = s.CharField(label=_('事件类型'), max_length=32, required=False)
    action = s.ChoiceField(label=_('事件操作'), choices=EventActions.member_list(), required=False)
    group = s.CharField(label=_('事件组名'), max_length=32, required=False, default=DEFAULT_ALL_GROUP_NAME)
    req_id = s.IntegerField(label=_('请求ID'), default=0, required=False)
    channel_name = s.CharField(label=_('通道名'), max_length=128, required=False)
    server_time = s.IntegerField(label=_('服务器时间'), required=False)


class ModelEventActions(EventActions):
    SAVE = 'save', _('保存')
    DELETE = 'delete', _('删除')


class ModelEventDataSer(EventDataSer):
    type = s.CharField(label=_('事件类型'), max_length=32, default='model_signal')
    action = s.ChoiceField(label=_('事件操作'), choices=ModelEventActions.member_list(), required=False)
    model = s.CharField(label=_('模型名称'), max_length=32, required=False)


class MessageEventDataSer(EventDataSer):
    type = s.CharField(label=_('事件类型'), max_length=32, default='system_message')
