# -*- coding: utf-8 -*-
# @Time: 2021-04-10 17:24:20.375300


from drf_yasg.utils import swagger_auto_schema
from framework.filters import MyFilterBackend, OrderingFilter, MyFilterSerializer
from framework.translation import _
from framework.route import Route
from framework.serializer import s,BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, ParamsSerializer, PaginationSerializer
from framework.views import CurdViewSet, ListPageNumberPagination, Response,action,Request
from framework.views import render_to_response as rt
from celery_task.models import SolarSchedule


class SolarScheduleSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/
    event_alias = s.CharField(source='get_event_display',required=False, read_only=True)
    alias = s.SerializerMethodField()

    def get_alias(self, obj):
        return str(obj)

    class Meta:
        model = SolarSchedule
        fields =  '__all__'
        #exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']
        #extra_kwargs = {'password': {'write_only': True}}


class ListSolarScheduleRspSerializer(PaginationSerializer):
    results = SolarScheduleSerializer(many=True)

@Route('celery_task/solar_schedule')
class SolarScheduleSet(CurdViewSet):
    filter_backends = (MyFilterBackend,OrderingFilter)

    serializer_class = SolarScheduleSerializer
    # 可条件过滤的字段
    filter_fields =  ['id', 'event', 'latitude', 'longitude']
    # 可排序的字段
    ordering_fields = ['id', 'event', 'latitude', 'longitude']
    # 可以查询字段
    queryset_fields = ['id', 'event', 'latitude', 'longitude']

    model = SolarSchedule

    def get_queryset(self):
        return SolarSchedule.objects.all().prefetch_related(*[]).select_related(*[]).only(*SolarScheduleSet.queryset_fields)

    @swagger_auto_schema(query_serializer=MyFilterSerializer,responses=ListSolarScheduleRspSerializer)
    def list(self, request):
        """SolarSchedule 列表"""
        return rt("celery_task/solar_schedule/list.html",super().list(request))

    @swagger_auto_schema(query_serializer=EditParams, responses=SolarScheduleSerializer)
    def edit(self, request):
        """SolarSchedule 编辑"""
        return rt("celery_task/solar_schedule/edit.html",super().edit(request))

    @swagger_auto_schema(query_serializer=IdSerializer,request_body=SolarScheduleSerializer, responses=SolarScheduleSerializer)
    def save(self, request):
        """SolarSchedule 保存"""
        return super().save(request)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request):
        """SolarSchedule 删除"""
        return super().delete(request)


    # @swagger_auto_schema(methods=['post'], request_body=SolarScheduleSerializer, responses=SolarScheduleSerializer)
    # @action(['post'])
    # def foo_action(self, request):
    #     return Response(SolarScheduleSerializer().data)