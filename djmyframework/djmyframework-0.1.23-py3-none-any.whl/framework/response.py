# -*- coding: utf-8 -*-
# @Time    : 2019-09-02 11:01
# @Author  : xzr
# @File    : response
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :
import logging
import re
from functools import lru_cache

from django.http import HttpResponse
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from rest_framework import serializers as s, status
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response as RestResponse

from .renderers import JSONRenderer
from .serializer import DataSerializer
from .translation import _
from .utils import json_dumps, ObjectDict, trace_msg
import time

SUCCESS_CODE = 0
FAIL_CODE = 1001
SUCCESS_MSG = _('OK')


class RspStruct(ObjectDict):
    """
    返回响应基本数据结构
    """
    code: int = SUCCESS_CODE
    msg: str = SUCCESS_MSG
    data: any = None


class RspData(RspStruct):
    def __init__(self, code=RspStruct.code, msg=RspStruct.msg, data=RspStruct.data):
        self.code = code
        self.msg = msg
        self.data = data
        self._t = int(time.time())

class RspSerializer(DataSerializer):
    code = s.ChoiceField(label=_("业务错误代码"), choices=[(RspStruct.code, RspStruct.msg)], default=RspStruct.code)
    msg = s.CharField(label=_("业务消息"), default=RspStruct.msg)
    data = s.DictField(label=_("业务数据"), required=False)


class Response(RestResponse):

    def __init__(self, data=RspStruct.data, template_name='', code=RspStruct.code, msg=RspStruct.msg, request=None,
                 *args, **kwargs):
        self.template_name = template_name
        self.request: Request = request
        self.context = RspData(data=data, code=code, msg=msg)
        self.set_data(data)

        super(Response, self).__init__(self.context, template_name=template_name, *args, **kwargs)

    def is_json(self):
        return self.request.is_json()

    def set_data(self, data):
        from .serializer import ParamsSerializer
        if isinstance(data, ParamsSerializer):
            data = data.get_set_data() or data.data
        if isinstance(data, s.BaseSerializer):
            data = data.data
        self.context.data = data

    def set_code(self, code):
        self.context.code = code

    def set_msg(self, msg):
        self.context.msg = msg

    def __call__(self, *args, **kwargs):
        return Response(*args, **kwargs)

    def resolve_json_data(self):
        if isinstance(self.context.data, dict):
            self.context.data.pop('self', '')
            self.context.data.pop('request', '')

    def resolve_data(self, request):
        if request.is_json():
            self.resolve_json_data()
        return self.context

    @property
    def rendered_content(self):
        renderer = getattr(self, 'accepted_renderer', None)
        renderer_context = getattr(self, 'renderer_context', None)
        # 通过 rest 视图类 或 api 方式返回,根据路径获取 template
        if renderer_context:
            request = renderer_context.get('request')
            url_config = request.resolver_match
            template_name = '%s.html' % '/'.join(re.split(r'\.', url_config.view_name))
            self.template_name = self.template_name or template_name

            self.resolve_data(request)
            try:
                return super(Response, self).rendered_content
            except TemplateDoesNotExist:
                logging.warning(trace_msg())
                self.resolve_json_data()
                return HttpResponse(json_dumps(self.context))

        else:
            if self.request:
                if self.request.is_json():
                    return HttpResponse(json_dumps(self.context))
            if self.template_name:
                return render(self.request, self.template_name, self.context)
            return HttpResponse(self.context)


class JsonResponse(Response):
    @property
    def rendered_content(self):
        setattr(self, 'accepted_renderer', JSONRenderer())
        return super(JsonResponse, self).rendered_content


class RspError(APIException):
    code = status_code = status.HTTP_200_OK
    msg = default_detail = _('rsp error.')
    default_code = 'rsp error'

    def __init__(self, detail=None, code=FAIL_CODE):
        """
        业务错误代码
        :param detail:
        :param code:
        """
        if isinstance(detail, int):
            detail, code = code, detail
        super(RspError, self).__init__(detail=detail, code=code)
        self.code = code
        self.msg = detail

    def __str__(self):
        return 'RspError(%s,%s)' % (self.code, self.msg)

    def __call__(self, msg):
        return RspError(msg, self.code)


class RspErrorEnum(object):

    @classmethod
    @lru_cache()
    def member_list(cls):
        return tuple((v.code, v.msg) for k, v in cls.__dict__.items() if isinstance(v, RspError))


def render_to_response(template_name, context=None, **kwargs):
    if isinstance(context, Response):
        context.template_name = context.template_name or template_name
        return context
    return Response(context, template_name=template_name, **kwargs)
