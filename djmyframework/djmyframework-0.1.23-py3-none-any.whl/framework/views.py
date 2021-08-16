#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# 视图的基本
#
# =========================================
import functools
import inspect
import types
from collections import OrderedDict

from django.conf import settings
from django.forms.utils import pretty_name
from django.http import Http404
from django.shortcuts import render as _render
from django.utils.translation import gettext_lazy as _
from django.views.i18n import set_language
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import MethodMapper
from rest_framework.metadata import SimpleMetadata
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

LANGUAGES = settings.LANGUAGES
from .filters import MyFilterBackend, OrderingFilter
from .route import Route
from .models import BaseModel
from .response import *
from .serializer import EditParams, IdSerializer, IdsSerializer

render = _render


def notauth(obj):
    """免登录认证标记
    """

    setattr(obj, 'notauth', True)
    return obj


def notcheck(obj):
    """免权限检查
    """

    setattr(obj, 'notcheck', True)
    return obj


def is_notauth(view_func):
    """免登陆验证"""
    return hasattr(view_func, 'notauth')


def is_notcheck(view_func):
    """免权限检查"""
    return is_notauth(view_func) or hasattr(view_func, 'notcheck')


def json_response(func):
    """返回json处理
    """

    @functools.wraps(func)
    def json_warp_func(*args, **kwargs):
        _r = {"code": -1, "msg": "", "data": []}
        response = func(*args, **kwargs)
        if isinstance(response, (tuple, list)):
            response_len = len(response)
            _r["code"] = response[0]
            if response_len >= 2:
                _r["msg"] = response[1]
            if response_len >= 3:
                _r["data"] = response[2]
            response = HttpResponse(json_dumps(_r))
        elif isinstance(response, dict):
            _r.update(response)
            response = HttpResponse(json_dumps(_r))
        return response

    return json_warp_func


def model_search(request, model_objects, search=None, order=None, page_size=20, page_num=0):
    order = order or ['id']
    _st = time.time()
    page_num = int(page_num)
    if page_num == 0:
        page_num = int(request.REQUEST.get('page_num', '1'))
        if page_num <= 0:
            page_num = 1
    total_record = 0
    total_page = 0

    model_list = {}

    page_size = int(request.REQUEST.get('page_size', page_size))

    page_size = 100 if page_size > 100 else page_size

    if hasattr(model_objects, 'objects'):
        model_objects = model_objects.objects

    if isinstance(search, dict):
        for k in search.keys():
            if not search[k]:
                del search[k]
        if len(search) != 0:
            count = model_objects.filter(**search).count()
        else:
            count = model_objects.count()
    else:
        count = model_objects.filter(search).count()

    if count > 0:
        total_record = count
        total_page = total_record / page_size
        if total_record % page_size >= 1:
            total_page = total_page + 1
        if page_num > total_page:
            pass
        else:
            if isinstance(search, dict):
                if len(search) != 0:
                    model_list = model_objects.filter(**search).order_by(*order)[
                                 page_size * (page_num - 1):page_size * page_num]
                else:
                    model_list = model_objects.order_by(*order)[page_size * (page_num - 1):page_size * page_num]
            else:
                model_list = model_objects.filter(search).order_by(*order)[
                             page_size * (page_num - 1):page_size * page_num]

    params = {
            "results"     : model_list,
            "page"        : page_num,
            "page_size"   : page_size,
            "total_record": total_record,
            "total_page"  : total_page,
            "use_time"    : time.time() - _st
    }
    return params


def api_view(http_method_names=None, detail=False):
    """
    Decorator that converts a function-based view into an APIView subclass.
    Takes a list of allowed methods for the view as an argument.
    """
    http_method_names = ['GET'] if (http_method_names is None) else http_method_names
    if not isinstance(http_method_names, (list, tuple)):
        http_method_names = [http_method_names]

    def decorator(func):
        WrappedAPIView: APIView = type(
                'WrappedAPIView',
                (APIView,),
                {'__doc__': func.__doc__}
        )
        WrappedAPIView.__annotations__ = func.__annotations__
        # Note, the above allows us to set the docstring.
        # It is the equivalent of:
        #
        #     class WrappedAPIView(APIView):
        #         pass
        #     WrappedAPIView.__doc__ = func.doc    <--- Not possible to do this

        # api_view applied without (method_names)
        assert not (isinstance(http_method_names, types.FunctionType)), \
            '@api_view missing list of allowed HTTP methods'

        # api_view applied with eg. string instead of list of strings
        assert isinstance(http_method_names, (list, tuple)), \
            '@api_view expected a list of strings, received %s' % type(http_method_names).__name__

        allowed_methods = set(http_method_names) | {'options'}
        WrappedAPIView.http_method_names = [method.lower() for method in allowed_methods]

        def handler(self, *args, **kwargs):
            return func(*args, **kwargs)

        for method in http_method_names:
            setattr(WrappedAPIView, method.lower(), handler)

        WrappedAPIView.__name__ = func.__name__
        WrappedAPIView.__module__ = func.__module__

        WrappedAPIView.renderer_classes = getattr(func, 'renderer_classes',
                                                  APIView.renderer_classes)

        WrappedAPIView.parser_classes = getattr(func, 'parser_classes',
                                                APIView.parser_classes)

        WrappedAPIView.authentication_classes = getattr(func, 'authentication_classes',
                                                        APIView.authentication_classes)

        WrappedAPIView.throttle_classes = getattr(func, 'throttle_classes',
                                                  APIView.throttle_classes)

        WrappedAPIView.permission_classes = getattr(func, 'permission_classes',
                                                    APIView.permission_classes)

        WrappedAPIView.schema = getattr(func, 'schema',
                                        APIView.schema)
        WrappedAPIView.annotations = func.__annotations__
        WrappedAPIView.is_api_view = True
        return WrappedAPIView.as_view()

    return decorator


def action(methods=None, detail=False, url_path=None, url_name=None, **kwargs):
    """
    Mark a ViewSet method as a routable action.

    Set the `detail` boolean to determine if this action should apply to
    instance/detail requests or collection/list requests.
    """
    methods = ['get'] if (methods is None) else methods
    if not isinstance(methods, (list, tuple)):
        methods = [methods]

    methods = [method.lower() for method in methods]

    assert detail is not None, (
            "@action() missing required argument: 'detail'"
    )

    # name and suffix are mutually exclusive
    if 'name' in kwargs and 'suffix' in kwargs:
        raise TypeError("`name` and `suffix` are mutually exclusive arguments.")

    def decorator(func):
        func.mapping = MethodMapper(func, methods)

        func.detail = detail
        func.url_path = url_path if url_path else func.__name__
        func.url_name = url_name if url_name else func.__name__
        func.kwargs = kwargs

        # Set descriptive arguments for viewsets
        if 'name' not in kwargs and 'suffix' not in kwargs:
            func.kwargs['name'] = pretty_name(func.__name__)
        func.kwargs['description'] = func.__doc__ or None

        return func

    return decorator

def api_action_judge(*args,**kwargs):

    def decorator(func):
        if inspect.getfullargspec(func).args[0] == 'self':
            return action(*args,**kwargs)(func)
        else:
            return api_view(*args, **kwargs)(func)
    return decorator

from .utils import DecoratorsPartial

action_get = DecoratorsPartial(api_action_judge, ['get'])
action_post = DecoratorsPartial(api_action_judge, ['post'])
action_get_post = DecoratorsPartial(api_action_judge, ['post', 'get'])

api_get = DecoratorsPartial(api_action_judge, 'get')
api_post = DecoratorsPartial(api_action_judge, 'post')

from django.views.generic import View


class BaseView(View):

    def _magic_prepare(self):
        self.get_arguments = self.request.REQUEST.getlist
        self.get_argument = self.request.REQUEST.get

    def get(self, *args, **kwrags):
        raise Exception('rewirte this method!')

    def post(self, *args, **kwrags): return self.get(*args, **kwrags)

    def put(self, *args, **kwrags): return self.get(*args, **kwrags)

    def delete(self, *args, **kwrags): return self.get(*args, **kwrags)

    def options(self, *args, **kwrags): return self.get(*args, **kwrags)

    def trace(self, *args, **kwrags): return self.get(*args, **kwrags)

    def filter_uri(self, path):
        return path.strip('_')

    def render(request, self, template_name, dict_value, *args, **kwargs):
        dict_value.update({"request": self.request})
        return render(self.request, template_name, dict_value, *args, **kwargs)

    def render_json(self, data):
        if isinstance(data, dict):
            data = json_dumps(data, ensure_ascii=False)
        return self.HttpResponse(data)

    def HttpResponse(self, *args, **kwargs):
        return HttpResponse(*args, **kwargs)

    @classmethod
    def as_view(cls, *args, **kw):
        return super(BaseView, cls).as_view(*args, **kw)


class BaseModelView(BaseView):
    """基本视图
    """

    deny_method_names = ['get', 'init', 'render', 'HttpResponse', 'initialize'] + \
                        ['post', 'put', 'delete', 'head', 'options', 'trace']

    model = None

    def get(self, request, path, *args, **kwargs):

        self.path = self.filter_uri(path)
        self._magic_prepare()
        if path not in self.deny_method_names:
            method = getattr(self, path, None)
            if hasattr(method, '__call__'):
                self.initialize()
                return method()

        return self._default()

    def _default(self):
        return HttpResponse('reject this view call %s!' % self.path)

    def initialize(self):
        """初始化
        """
        pass


class ListPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 200
    page_query_description = _('页码,第几页')
    page_size_query_description = _('每页返回数量')

    def get_paginated_response(self, data):
        data = OrderedDict(
                count=self.page.paginator.count,
                next=self.get_next_link(),
                previous=self.get_previous_link(),
                page=self.request.query_params.get(self.page_query_param, 1),
                page_size=self.get_page_size(self.request),
                results=data,
                filter=self.request.query_params
        )
        return Response(data)


class BaseViewSet(viewsets.GenericViewSet):
    serializer_class = RspSerializer
    response: Response = None

    def initial(self, request: Request, *args, **kwargs):
        self.response = Response()

        return super(BaseViewSet, self).initial(request, *args, **kwargs)

    def is_post(self):
        return self.request.is_post()

    def is_get(self):
        return self.request.is_get()

    def is_ajax(self):
        return self.request.is_ajax()

    def is_json(self):
        return self.request.is_json()

    @notcheck
    def metadata(self, request, *args, **kwargs):
        """
        获取模型定义
        """
        view = self
        metadata = OrderedDict()
        metadata['name'] = view.get_view_name()
        metadata['description'] = view.get_view_description()
        metadata['parses'] = [parser.media_type for parser in view.parser_classes]

        if self.serializer_class:
            simple_meta = SimpleMetadata()
            serializer = view.get_serializer().to_schema()
            # metadata['serializer'] = simple_meta.get_serializer_info(serializer)
            metadata['serializer'] = view.get_serializer().to_schema()
        data = metadata
        return Response(data, template_name='framework/metadata.html')


class CurdViewSet(BaseViewSet):
    pagination_class = ListPageNumberPagination
    filter_backends = (MyFilterBackend, OrderingFilter)
    model: BaseModel
    request: Request
    model_instance = None

    queryset_fields = None

    def get_model_instance(self, params_cls=IdSerializer, queryset=None):
        if self.model_instance is not None:
            return self.model_instance
        self.request.query_params.update(self.request.data)
        req_params = self.request.query_params
        query_params = params_cls(data=req_params).params_data
        if not query_params.id:
            self.model_instance = self.model()
        else:
            _queryset = self.get_queryset()
            try:
                if queryset is not None:
                    _queryset = queryset
                # self.model_instance = get_object_or_404(queryset or self.model, id=query_params.id)
                self.model_instance = _queryset.get(id=query_params.id)
            except _queryset.model.DoesNotExist:
                raise Http404('No %s matches the given query.' % _queryset.model._meta.object_name)
        return self.model_instance

    def list(self, request: Request):
        """
        查询
        """
        if not self.is_ajax() and not self.is_json():
            return Response(self.get_serializer_class()())
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, fields=self.queryset_fields)
        return self.get_paginated_response(serializer.data)

    @property
    def is_copy(self):
        return self.request.query_params.get('is_copy', False)

    @swagger_auto_schema(query_serializer=EditParams)
    def edit(self, request: Request):
        """
        编辑
        """
        model_instance = self.get_model_instance(EditParams)
        serializer = self.get_serializer(instance=model_instance)
        if not model_instance.id:
            serializer.data.update(request.query_params)
        return self.response(serializer.data)

    def save_instance(self, request, model_instance=None, **kwargs):
        msg = _("保存成功")
        edit_params = EditParams(self.request.query_params).params_data
        model_instance = model_instance or self.get_model_instance(EditParams)
        if self.is_copy:
            model_instance = self.model()
        partial = True if model_instance.id else False
        serializer = self.get_serializer(instance=model_instance, data=request.data, partial=partial)
        if self.is_copy:
            msg = _("复制成功")
        serializer.is_valid(raise_exception=True)

        serializer.save(**kwargs)
        if getattr(model_instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            model_instance._prefetched_objects_cache = {}
        return serializer, msg

    def save(self, request: Request, *args, **kwargs):
        """
        保存
        """
        serializer, msg = self.save_instance(request)
        return Response(serializer.data, msg=msg)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request: Request):
        """
        删除
        """

        params = IdsSerializer(request.data).params_data

        if params.id:
            ids = params.id
            self.get_queryset().filter(id__in=ids).delete()
            return Response(data=params)

        return Response(params, msg=_('ids empty'))


@Route('i18n')
class I18n(BaseViewSet):
    """
    国际语言
    """

    class SetLanguageSerializer(s.Serializer):
        next = s.CharField(label=_('跳转页面'), required=False)
        language = s.ChoiceField(label=_('语言代码'), choices=LANGUAGES, required=True)

    @notcheck
    @swagger_auto_schema(request_body=SetLanguageSerializer)
    @action('post')
    def set_language(self, request):
        """
        设置语言环境
        """
        return set_language(request)

    @notauth
    @action('get')
    def js(self, request):
        """js语言切换,加载
        <script type="text/javascript" src="/i18n/js?format=html"></script>
        """
        from .filters import ConditionTypeEnum
        condition_schema = ConditionTypeEnum.get_schema()
        return render_to_response('framework/i18n_js.html', locals(), content_type='application/javascript')
