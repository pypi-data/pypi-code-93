# -*- coding: utf-8 -*-
# @Time: 2021-04-10 15:07:57.560595


from drf_yasg.utils import swagger_auto_schema
from framework.filters import MyFilterBackend, OrderingFilter, MyFilterSerializer
from framework.translation import _
from framework.route import Route
from framework.serializer import s,BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, ParamsSerializer, PaginationSerializer
from framework.views import CurdViewSet, ListPageNumberPagination, Response,action,Request
from framework.views import render_to_response as rt
from celery_task.models import IntervalSchedule


class IntervalScheduleSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/
    period_alias = s.CharField(source='get_period_display',required=False, read_only=True)

    alias = s.SerializerMethodField()

    def get_alias(self, obj):
        return str(obj)

    class Meta:
        model = IntervalSchedule
        fields = '__all__'
        #exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']
        #extra_kwargs = {'password': {'write_only': True}}


class ListIntervalScheduleRspSerializer(PaginationSerializer):
    results = IntervalScheduleSerializer(many=True)

@Route('celery_task/interval_schedule')
class IntervalScheduleSet(CurdViewSet):
    filter_backends = (MyFilterBackend,OrderingFilter)

    serializer_class = IntervalScheduleSerializer
    # 可条件过滤的字段
    filter_fields =  ['id', 'every', 'period']
    # 可排序的字段
    ordering_fields = ['id', 'every', 'period']
    # 可以查询字段
    queryset_fields = ['id', 'every', 'period']

    model = IntervalSchedule

    def get_queryset(self):
        return IntervalSchedule.objects.all().prefetch_related(*[]).select_related(*[]).only(*IntervalScheduleSet.queryset_fields)

    @swagger_auto_schema(query_serializer=MyFilterSerializer,responses=ListIntervalScheduleRspSerializer)
    def list(self, request):
        """IntervalSchedule 列表"""
        return rt("celery_task/interval_schedule/list.html",super().list(request))

    @swagger_auto_schema(query_serializer=EditParams, responses=IntervalScheduleSerializer)
    def edit(self, request):
        """IntervalSchedule 编辑"""
        return rt("celery_task/interval_schedule/edit.html",super().edit(request))

    @swagger_auto_schema(query_serializer=IdSerializer,request_body=IntervalScheduleSerializer, responses=IntervalScheduleSerializer)
    def save(self, request):
        """IntervalSchedule 保存"""
        return super().save(request)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request):
        """IntervalSchedule 删除"""
        return super().delete(request)


    # @swagger_auto_schema(methods=['post'], request_body=IntervalScheduleSerializer, responses=IntervalScheduleSerializer)
    # @action(['post'])
    # def foo_action(self, request):
    #     return Response(IntervalScheduleSerializer().data)