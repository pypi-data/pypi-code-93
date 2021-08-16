# -*- coding: utf-8 -*-

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_delete, post_save

from framework.models import BaseModel
from ..serializer import ModelEventActions, ModelEventDataSer
from ..settings import SUBSCRIBE_MODEL_CHANGE


def group_send(group_name, event_data):
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(group_name, event_data)


def model_post_save_signal(sender, instance, created, **kwargs):
    if isinstance(instance, BaseModel):
        group_name = sender.get_table_name()
        event = ModelEventDataSer()
        event.o.group = group_name
        event.o.model = group_name
        event.o.action = ModelEventActions.SAVE
        event.o.data = instance.to_dict(is_msgpack=True)
        group_send(group_name, event.data)


def model_post_delete_signal(sender, instance, **kwargs):
    if isinstance(instance, BaseModel):
        group_name = sender.get_table_name()
        event = ModelEventDataSer()
        event.o.group = group_name
        event.o.model = group_name
        event.o.action = ModelEventActions.DELETE
        event.o.data = instance.to_dict(has_m2mfields=False, is_msgpack=True)
        group_send(group_name, event.data)


if SUBSCRIBE_MODEL_CHANGE:
    post_save.connect(model_post_save_signal, dispatch_uid="all_model_post_save")
    post_delete.connect(model_post_delete_signal, dispatch_uid="all_model_post_delete")
