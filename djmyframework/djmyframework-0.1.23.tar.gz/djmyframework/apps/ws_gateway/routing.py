# -*- coding: utf-8 -*-
# @Time    : 2021-03-24 16:53
# @Author  : xzr
# @File    : routing
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 


from django.urls import re_path

from . import ws_gateway_consumers

websocket_urlpatterns = [
    re_path(r'^ws[/]?$', ws_gateway_consumers.WebsocketGateWayConsumer.as_asgi()),
]