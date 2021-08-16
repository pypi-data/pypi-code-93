# -*- coding: utf-8 -*-
# @Time: 2021-04-10 15:24:40.185140


from drf_yasg.utils import swagger_auto_schema
from framework.filters import MyFilterBackend, OrderingFilter, MyFilterSerializer
from framework.translation import _
from framework.route import Route
from framework.serializer import s,BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, ParamsSerializer, PaginationSerializer
from framework.views import CurdViewSet, ListPageNumberPagination, Response,action,Request
from framework.views import render_to_response as rt
from celery_task.models import ClockedSchedule


class ClockedScheduleSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/
    alias = s.SerializerMethodField()

    def get_alias(self, obj):
        return str(obj)

    class Meta:
        model = ClockedSchedule
        fields =   '__all__'
        #exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']
        #extra_kwargs = {'password': {'write_only': True}}


class ListClockedScheduleRspSerializer(PaginationSerializer):
    results = ClockedScheduleSerializer(many=True)

@Route('celery_task/clocked_schedule')
class ClockedScheduleSet(CurdViewSet):
    filter_backends = (MyFilterBackend,OrderingFilter)

    serializer_class = ClockedScheduleSerializer
    # 可条件过滤的字段
    filter_fields =  ['id', 'clocked_time']
    # 可排序的字段
    ordering_fields = ['id', 'clocked_time']
    # 可以查询字段
    queryset_fields = ['id', 'clocked_time']

    model = ClockedSchedule

    def get_queryset(self):
        return ClockedSchedule.objects.all().prefetch_related(*[]).select_related(*[]).only(*ClockedScheduleSet.queryset_fields)

    @swagger_auto_schema(query_serializer=MyFilterSerializer,responses=ListClockedScheduleRspSerializer)
    def list(self, request):
        """ClockedSchedule 列表"""
        return rt("celery_task/clocked_schedule/list.html",super().list(request))

    @swagger_auto_schema(query_serializer=EditParams, responses=ClockedScheduleSerializer)
    def edit(self, request):
        """ClockedSchedule 编辑"""
        return rt("celery_task/clocked_schedule/edit.html",super().edit(request))

    @swagger_auto_schema(query_serializer=IdSerializer,request_body=ClockedScheduleSerializer, responses=ClockedScheduleSerializer)
    def save(self, request):
        """ClockedSchedule 保存"""
        return super().save(request)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request):
        """ClockedSchedule 删除"""
        return super().delete(request)


    # @swagger_auto_schema(methods=['post'], request_body=ClockedScheduleSerializer, responses=ClockedScheduleSerializer)
    # @action(['post'])
    # def foo_action(self, request):
    #     return Response(ClockedScheduleSerializer().data)