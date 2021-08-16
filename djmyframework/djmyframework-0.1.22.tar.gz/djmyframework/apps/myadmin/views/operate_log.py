# -*- coding: utf-8 -*-
# @Time: 2020-06-05 16:11:30.758328


from drf_yasg.utils import swagger_auto_schema
from framework.filters import MyFilterBackend, OrderingFilter, MyFilterSerializer
from django.utils.translation import gettext_lazy as _
from framework.route import Route
from framework.serializer import s,BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, ParamsSerializer, PaginationSerializer
from framework.filters import MyFilterBackend
from framework.views import CurdViewSet, ListPageNumberPagination, Response,action
from myadmin.models import OperateLog


class OperateLogSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/


    class Meta:
        model = OperateLog
        fields =  ['id', 'user_id', 'type', 'ip', 'full_path', 'post_params', 'msg', 'user_agent', 'create_datetime', 'update_datetime'] or '__all__'
        #exclude = ['session_key']
        #read_only_fields = []



class ListOperateLogRspSerializer(PaginationSerializer):
    results = OperateLogSerializer(many=True)

@Route('myadmin/operate_log')
class OperateLogSet(CurdViewSet):
    filter_backends = (MyFilterBackend,OrderingFilter)

    serializer_class = OperateLogSerializer
    # 可条件过滤的字段
    filter_fields =  ['id', 'user_id', 'type', 'ip', 'full_path', 'post_params', 'msg', 'user_agent', 'create_datetime', 'update_datetime']
    # 可排序的字段
    ordering_fields = ['id', 'user_id', 'type', 'ip', 'full_path', 'post_params', 'msg', 'user_agent', 'create_datetime', 'update_datetime']

    model = OperateLog

    def get_queryset(self):
        return OperateLog.objects.all().prefetch_related(*[]).select_related(*[])

    @swagger_auto_schema(query_serializer=MyFilterSerializer,responses=ListOperateLogRspSerializer)
    def list(self, request, *args, **kwargs):
        return super(OperateLogSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(query_serializer=EditParams, responses=OperateLogSerializer)
    def edit(self, request, *args, **kwargs):
        return super(OperateLogSet, self).edit(request, *args, **kwargs)

    @swagger_auto_schema(query_serializer=IdSerializer,request_body=OperateLogSerializer, responses=OperateLogSerializer)
    def save(self, request, *args, **kwargs):
        return super(OperateLogSet, self).save(request, *args, **kwargs)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request, *args, **kwargs):
        return super(OperateLogSet, self).delete(request, *args, **kwargs)


    # @swagger_auto_schema(methods=['post'], request_body=OperateLogSerializer, responses=OperateLogSerializer)
    # @action(['post'])
    # def foo_action(self, request):
    #     return Response(OperateLogSerializer().data)