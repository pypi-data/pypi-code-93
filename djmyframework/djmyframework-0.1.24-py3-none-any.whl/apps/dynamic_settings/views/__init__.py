# -*- coding: utf-8 -*-

from framework.route import Route
from framework.views import api_get, api_post, render_to_response, Request, Response
from ..conf import settings_manager


@Route
@api_get
def list(request: Request):
    """动态配置"""
    data = settings_manager.group_options_map
    return render_to_response('dynamic_settimgs/list.html', data, request=request)


@Route
@api_post
def save(request: Request):
    """保存动态配置"""
    settings_data = request.data.get('settings_data', {})
    if settings_data:
        for k, v in settings_data.items():
            if settings_manager.settings_options_map.get(k, None) is not None:
                settings_manager.set_value(k, v)
    return Response()
