# -*- coding: utf-8 -*-
# @Time: 2021-04-10 17:23:10.562202


from drf_yasg.utils import swagger_auto_schema
from framework.filters import MyFilterBackend, OrderingFilter, MyFilterSerializer
from framework.translation import _
from framework.route import Route
from framework.serializer import s,BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, ParamsSerializer, PaginationSerializer
from framework.views import CurdViewSet, ListPageNumberPagination, Response,action,Request
from framework.views import render_to_response as rt
from celery_task.models import PeriodicTask


class PeriodicTaskSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/
    #interval = s.RelatedField(label=_("Interval Schedule"),queryset=PeriodicTask.interval.field.related_model.objects.all())
    #crontab = s.RelatedField(label=_("Crontab Schedule"),queryset=PeriodicTask.crontab.field.related_model.objects.all())
    #solar = s.RelatedField(label=_("Solar Schedule"),queryset=PeriodicTask.solar.field.related_model.objects.all())
    #clocked = s.RelatedField(label=_("Clocked Schedule"),queryset=PeriodicTask.clocked.field.related_model.objects.all())
    alias = s.SerializerMethodField()

    def get_alias(self, obj):
        return str(obj)
    class Meta:
        model = PeriodicTask
        fields =  ['id', 'name', 'alias','task', 'interval', 'crontab', 'solar', 'clocked', 'args', 'kwargs', 'queue', 'exchange', 'routing_key', 'headers', 'priority', 'expires', 'expire_seconds', 'one_off', 'start_time', 'enabled', 'last_run_at', 'total_run_count', 'date_changed', 'description'] or '__all__'
        #exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']
        #extra_kwargs = {'password': {'write_only': True}}


class ListPeriodicTaskRspSerializer(PaginationSerializer):
    results = PeriodicTaskSerializer(many=True)

@Route('celery_task/periodic_task')
class PeriodicTaskSet(CurdViewSet):
    filter_backends = (MyFilterBackend,OrderingFilter)

    serializer_class = PeriodicTaskSerializer
    # 可条件过滤的字段
    filter_fields =  ['id', 'name', 'task', 'interval', 'crontab', 'solar', 'clocked', 'args', 'kwargs', 'queue', 'exchange', 'routing_key', 'headers', 'priority', 'expires', 'expire_seconds', 'one_off', 'start_time', 'enabled', 'last_run_at', 'total_run_count', 'date_changed', 'description']
    # 可排序的字段
    ordering_fields = ['id', 'name', 'task', 'interval', 'crontab', 'solar', 'clocked', 'args', 'kwargs', 'queue', 'exchange', 'routing_key', 'headers', 'priority', 'expires', 'expire_seconds', 'one_off', 'start_time', 'enabled', 'last_run_at', 'total_run_count', 'date_changed', 'description']
    # 可以查询字段
    queryset_fields = ['id', 'name', 'task', 'interval', 'crontab', 'solar', 'clocked', 'args', 'kwargs', 'queue', 'exchange', 'routing_key', 'headers', 'priority', 'expires', 'expire_seconds', 'one_off', 'start_time', 'enabled', 'last_run_at', 'total_run_count', 'date_changed', 'description']

    model = PeriodicTask

    def get_queryset(self):
        return PeriodicTask.objects.all().prefetch_related(*[]).select_related(*['interval', 'crontab', 'solar', 'clocked']).only(*PeriodicTaskSet.queryset_fields)

    @swagger_auto_schema(query_serializer=MyFilterSerializer,responses=ListPeriodicTaskRspSerializer)
    def list(self, request):
        """PeriodicTask 列表"""
        return rt("celery_task/periodic_task/list.html",super().list(request))

    @swagger_auto_schema(query_serializer=EditParams, responses=PeriodicTaskSerializer)
    def edit(self, request):
        """PeriodicTask 编辑"""
        return rt("celery_task/periodic_task/edit.html",super().edit(request))

    @swagger_auto_schema(query_serializer=IdSerializer,request_body=PeriodicTaskSerializer, responses=PeriodicTaskSerializer)
    def save(self, request):
        """PeriodicTask 保存"""
        return super().save(request)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request):
        """PeriodicTask 删除"""
        return super().delete(request)


    # @swagger_auto_schema(methods=['post'], request_body=PeriodicTaskSerializer, responses=PeriodicTaskSerializer)
    # @action(['post'])
    # def foo_action(self, request):
    #     return Response(PeriodicTaskSerializer().data)