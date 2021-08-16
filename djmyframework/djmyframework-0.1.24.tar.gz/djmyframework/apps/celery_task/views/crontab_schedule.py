# -*- coding: utf-8 -*-
# @Time: 2021-04-10 15:58:45.061262


from drf_yasg.utils import swagger_auto_schema
from framework.filters import MyFilterBackend, OrderingFilter, MyFilterSerializer
from framework.translation import _
from framework.route import Route
from framework.serializer import s,BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, ParamsSerializer, PaginationSerializer
from framework.views import CurdViewSet, ListPageNumberPagination, Response,action,Request
from framework.views import render_to_response as rt
from celery_task.models import CrontabSchedule


class CrontabScheduleSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/
    timezone_alias = s.CharField(source='get_timezone_display',required=False, read_only=True)
    alias = s.SerializerMethodField()

    timezone = s.CharField(required=False)

    def get_alias(self, obj):
        return str(obj)

    class Meta:
        model = CrontabSchedule
        fields =   '__all__'
        #exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']
        #extra_kwargs = {'password': {'write_only': True}}


class ListCrontabScheduleRspSerializer(PaginationSerializer):
    results = CrontabScheduleSerializer(many=True)


@Route('celery_task/crontab_schedule')
class CrontabScheduleSet(CurdViewSet):
    filter_backends = (MyFilterBackend,OrderingFilter)

    serializer_class = CrontabScheduleSerializer
    # 可条件过滤的字段
    filter_fields =  ['id', 'minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year', 'timezone']
    # 可排序的字段
    ordering_fields = ['id', 'minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year','timezone' ]
    # 可以查询字段
    queryset_fields = ['id', 'minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year','timezone' ]

    model = CrontabSchedule

    def get_queryset(self):
        return CrontabSchedule.objects.all().prefetch_related(*[]).select_related(*[]).only(*CrontabScheduleSet.queryset_fields)

    @swagger_auto_schema(query_serializer=MyFilterSerializer,responses=ListCrontabScheduleRspSerializer)
    def list(self, request):
        """CrontabSchedule 列表"""
        return rt("celery_task/crontab_schedule/list.html",super().list(request))

    @swagger_auto_schema(query_serializer=EditParams, responses=CrontabScheduleSerializer)
    def edit(self, request):
        """CrontabSchedule 编辑"""
        return rt("celery_task/crontab_schedule/edit.html",super().edit(request))

    @swagger_auto_schema(query_serializer=IdSerializer,request_body=CrontabScheduleSerializer, responses=CrontabScheduleSerializer)
    def save(self, request):
        """CrontabSchedule 保存"""
        return super().save(request)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request):
        """CrontabSchedule 删除"""
        return super().delete(request)


    # @swagger_auto_schema(methods=['post'], request_body=CrontabScheduleSerializer, responses=CrontabScheduleSerializer)
    # @action(['post'])
    # def foo_action(self, request):
    #     return Response(CrontabScheduleSerializer().data)