# -*- coding: utf-8 -*-
# @Time: 2020-06-15 17:42:57.318532


from drf_yasg.utils import swagger_auto_schema
from framework.filters import MyFilterBackend, OrderingFilter, MyFilterSerializer
from django.utils.translation import gettext_lazy as _
from framework.route import Route
from framework.serializer import s,BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, ParamsSerializer, PaginationSerializer
from framework.views import CurdViewSet, ListPageNumberPagination, Response,action
from ..models import LogDefine


class LogDefineSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/
    status_alias = s.CharField(source='get_status_display',required=False, read_only=True)

    class Meta:
        model = LogDefine
        fields =  ['id', 'name', 'key', 'config','remark', 'status', 'trigger', 'create_datetime', 'update_datetime', 'status_alias'] or '__all__'
        #exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']



class ListLogDefineRspSerializer(PaginationSerializer):
    results = LogDefineSerializer(many=True)

@Route('log_def/log_define')
class LogDefineSet(CurdViewSet):
    filter_backends = (MyFilterBackend,OrderingFilter)

    serializer_class = LogDefineSerializer
    # 可条件过滤的字段
    filter_fields =  ['id', 'name', 'key', 'remark', 'trigger', 'create_datetime', 'update_datetime' ]
    # 可排序的字段
    ordering_fields = ['id', 'name', 'key', 'remark', 'trigger', 'create_datetime', 'update_datetime' ]

    model = LogDefine

    def get_queryset(self):
        return LogDefine.objects.all().prefetch_related(*[]).select_related(*[])

    @swagger_auto_schema(query_serializer=MyFilterSerializer,responses=ListLogDefineRspSerializer)
    def list(self, request, *args, **kwargs):
        """日志类定义 列表"""
        return super(LogDefineSet, self).list(request, *args, **kwargs)

    class LogDefineEditParmas(EditParams):
        log_key = s.CharField(required=False)

    @swagger_auto_schema(query_serializer=EditParams, responses=LogDefineSerializer)
    def edit(self, request, *args, **kwargs):
        """日志类定义 编辑"""

        params = self.LogDefineEditParmas(request.query_params).params_data
        if params.log_key:

            model_instance = LogDefine.objects.get(key=params.log_key)
        else:
            model_instance = self.get_model_instance(EditParams)
        serializer = self.get_serializer(instance=model_instance)
        return self.response(serializer.data)

    @swagger_auto_schema(query_serializer=IdSerializer,request_body=LogDefineSerializer, responses=LogDefineSerializer)
    def save(self, request, *args, **kwargs):
        """日志类定义 保存"""
        model_instance = self.get_model_instance(IdSerializer)
        model_instance.config = request.data.get('config',{})
        serializer, msg = self.save_instance(request)
        return self.response(serializer.data, msg=msg)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request, *args, **kwargs):
        return super(LogDefineSet, self).delete(request, *args, **kwargs)


    # @swagger_auto_schema(methods=['post'], request_body=LogDefineSerializer, responses=LogDefineSerializer)
    # @action(['post'])
    # def foo_action(self, request):
    #     return Response(LogDefineSerializer().data)


