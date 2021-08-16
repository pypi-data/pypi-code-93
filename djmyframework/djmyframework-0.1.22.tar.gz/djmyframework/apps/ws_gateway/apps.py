# -*- coding: utf-8 -*-

from django.apps import AppConfig

from framework.translation import _


class WsGatewayConfig(AppConfig):
    name = 'ws_gateway'
    verbose_name = _('WebSocket 网关')
