# -*- coding: utf-8 -*-
# @Time: 2021-04-10 21:47:41.103769


from drf_yasg.utils import swagger_auto_schema
from framework.filters import MyFilterBackend, OrderingFilter, MyFilterSerializer
from framework.translation import _
from framework.route import Route
from framework.serializer import s,BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, ParamsSerializer, PaginationSerializer
from framework.views import CurdViewSet, ListPageNumberPagination, Response,action,Request
from framework.views import render_to_response as rt
from celery_task.models import TaskResult


class TaskResultSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/
    status_alias = s.CharField(source='get_status_display',required=False, read_only=True)

    class Meta:
        model = TaskResult
        fields =  ['id', 'task_id', 'task_name', 'task_args', 'task_kwargs', 'status', 'worker', 'content_type', 'content_encoding', 'result', 'date_created', 'date_done', 'traceback', 'meta', 'status_alias'] or '__all__'
        #exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']
        #extra_kwargs = {'password': {'write_only': True}}


class ListTaskResultRspSerializer(PaginationSerializer):
    results = TaskResultSerializer(many=True)

@Route('celery_task/task_result')
class TaskResultSet(CurdViewSet):
    filter_backends = (MyFilterBackend,OrderingFilter)

    serializer_class = TaskResultSerializer
    # 可条件过滤的字段
    filter_fields =  ['id', 'task_id', 'task_name', 'task_args', 'task_kwargs', 'status', 'worker', 'content_type', 'content_encoding', 'result', 'date_created', 'date_done', 'traceback', 'meta']
    # 可排序的字段
    ordering_fields = ['id', 'task_id', 'task_name', 'task_args', 'task_kwargs', 'status', 'worker', 'content_type', 'content_encoding', 'result', 'date_created', 'date_done', 'traceback', 'meta']
    # 可以查询字段
    queryset_fields = ['id', 'task_id', 'task_name', 'task_args', 'task_kwargs', 'status', 'worker', 'content_type', 'content_encoding', 'result', 'date_created', 'date_done', 'traceback', 'meta']

    model = TaskResult

    def get_queryset(self):
        return TaskResult.objects.all().prefetch_related(*[]).select_related(*[]).only(*TaskResultSet.queryset_fields)

    @swagger_auto_schema(query_serializer=MyFilterSerializer,responses=ListTaskResultRspSerializer)
    def list(self, request):
        """TaskResult 列表"""
        return rt("celery_task/task_result/list.html",super().list(request))

    @swagger_auto_schema(query_serializer=EditParams, responses=TaskResultSerializer)
    def edit(self, request):
        """TaskResult 编辑"""
        return rt("celery_task/task_result/edit.html",super().edit(request))

    @swagger_auto_schema(query_serializer=IdSerializer,request_body=TaskResultSerializer, responses=TaskResultSerializer)
    def save(self, request):
        """TaskResult 保存"""
        return super().save(request)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request):
        """TaskResult 删除"""
        return super().delete(request)


    # @swagger_auto_schema(methods=['post'], request_body=TaskResultSerializer, responses=TaskResultSerializer)
    # @action(['post'])
    # def foo_action(self, request):
    #     return Response(TaskResultSerializer().data)