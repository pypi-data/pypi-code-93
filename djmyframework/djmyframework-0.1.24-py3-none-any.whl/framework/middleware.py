# -*- coding: utf-8 -*-
import copy
import logging
import sys
import time

from django.http import Http404, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import exceptions, status
from rest_framework.views import set_rollback

from rest_framework.exceptions import PermissionDenied, ValidationError
from settings import DEBUG,LANGUAGE_CODE
from .utils import json_dumps, trace_msg
from .response import Response, RspData
from django.http.request import HttpRequest
_log = logging.getLogger('root')


def get_real_ip(request):
    """获取真实ip
    """
    return request.META.get('HTTP_REMOTE_ADDR2', '') or request.META.get('HTTP_X_FORWARDED_FOR',
                                                                         '') or request.META.get('REMOTE_ADDR')


class BaseMiddleware(MiddlewareMixin):
    """自定义request处理,增加一些方法和属性
    """

    def process_request(self, request):
        request.POST._mutable = True  #
        request.GET._mutable = True  # 可以使用reuqest.GET.setlist('key',[value])方法
        request.real_ip = get_real_ip(request)
        request.is_debug = DEBUG
        request._start_time = time.time()
        request.language = request.session.get('_language', '') or request.LANGUAGE_CODE or LANGUAGE_CODE
        request.language = request.language.lower()
        request.is_post = lambda :request.method == 'POST'
        request.is_get = lambda :request.method == 'GET'
        request.is_json = lambda :'json' in request.content_type or request.path.endswith('.json') or request.is_ajax() or request.GET.get('format','') == 'json'
        # 兼容以前功能
        request.REQUEST = copy.copy(request.POST)
        request.REQUEST.update(request.GET)


    def get_check_view_func(self, request, view_func):
        view_module = sys.modules.get(view_func.__module__, None)

        if view_module:
            view_actions = getattr(view_func, 'actions', None)
            check_view_func = getattr(view_module, view_func.__name__, view_func)
            if view_actions:
                action_name = view_actions.get(request.method.lower(), '')
                if action_name:
                    check_view_func = getattr(view_func.cls, action_name, None)

            return check_view_func

    def process_view(self, request, view_func, view_args, view_kwargs):

        pass

    def process_response(self, request, response):
        return response

    def process_template_response(self, request, response):
        """
        模板渲染前,增加返回code,和msg结构
        :param request:
        :param response:
        :return:
        """

        return response

    def process_exception(self, request, exception):
        """出错处理
        """
        msg = trace_msg()
        _log.warning(msg)
        if request.is_ajax():
            rsp = RspData(code=status.HTTP_500_INTERNAL_SERVER_ERROR, msg=msg)
            return HttpResponse(json_dumps(rsp), status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content_type='application/json')


# API 错误处理
def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    #elif isinstance(exc, PermissionDenied):
    #    exc = exceptions.PermissionDenied()

    #elif isinstance(exc, ValidationError):
     #   exc = exceptions.ValidationError(exc.message_dict)

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        data = None
        exc_status_msg = exc.default_detail
        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            exc_status_msg = exc.detail
        # 业务错误,http 都返回200
        status_code = status.HTTP_200_OK # exc.status_code
        set_rollback()

        rsp = Response(data, code=getattr(exc, 'code', exc.status_code), msg=exc_status_msg, status=status_code,
                       headers=headers,
                       template_name='api_exception.html')

        return rsp
    return None
