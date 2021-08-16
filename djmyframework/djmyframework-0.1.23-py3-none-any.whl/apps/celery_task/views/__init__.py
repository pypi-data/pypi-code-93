from celery import Task
from celery.result import AsyncResult
from django.db.models import Q
from django_celery_results.models import TaskResult
from drf_yasg.utils import swagger_auto_schema

from framework.route import Route
from framework.serializer import BaseModelSerializer, DataSerializer, ListIntField, ListStrField, ParamsSerializer, s
from framework.translation import _
from framework.views import action, action_get, BaseViewSet, JsonResponse, notcheck, ObjectDict, render_to_response, \
    Request
from celery_task.models import AssociatedTaskResult, states


class CeleryTaskSerializer(BaseModelSerializer):
    class Meta:
        model = TaskResult
        fields = ['id', 'task_id', 'task_name', 'result', 'status', 'date_done', 'meta', 'traceback']
        # exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']


class AssociatedTaskResultSer(BaseModelSerializer):
    is_all_done = s.BooleanField(label=_('是否都完成'), required=True)
    task_result_id = ListStrField(label=_('Celery任务ID'), help_text=_('celery task id 列表'))

    class Meta:
        model = AssociatedTaskResult
        fields = ['id', 'a_id', 'a_type_name', 'is_all_done', 'create_datetime', 'task_result_id']


class TaskIdMapSerializer(DataSerializer):
    idmap = s.DictField(label=_('任务状态 Map,通过 task id 获取启动状态'), required=False, default={})


@Route('celery_task')
class CeleryTask(BaseViewSet):
    # swagger_schema = None
    serializer_class = CeleryTaskSerializer

    class CeleryTaskQueryParams(ParamsSerializer):
        task_id = s.ListField(label='Celery任务ID列表', child=s.CharField(), help_text=_('celery 任务ID列表'), required=True)

    @notcheck
    @action_get()
    def test(self, request):
        """测试 celery 任务能否提交"""
        from ..tasks import test_live

        try:
            s: AsyncResult = test_live.delay()
            return JsonResponse(msg='ok', data=True)
        except Task.OperationalError as e:
            return JsonResponse(code=1, msg=str(e), data=False)

    @notcheck
    @action_get()
    def js(self, request):
        """Celery任务js库"""
        return render_to_response('celery_task/celery_task.js', AssociatedTaskResult,
                                  content_type='application/javascript')

    @swagger_auto_schema(query_serializer=CeleryTaskQueryParams, responses=CeleryTaskQueryParams)
    @action('post')
    def revoke_task(self, request: Request):
        """
        撤销 Celery 任务
        """
        from celery_app import app
        params = self.CeleryTaskQueryParams(request.data).params_data

        for t_id in params.task_id:
            app.control.revoke(t_id, terminate=True)
        TaskResult.objects.filter(task_id__in=params.task_id).update(status=states.REVOKED)
        return JsonResponse(params, request=request)

    class AssociatedTaskResultQueryParmas(ParamsSerializer):
        a_id = ListIntField(label=_('任务关联ID'), required=False)
        a_type_name = s.CharField(label=_('任务类型名'), required=False)
        is_done = s.BooleanField(label=_('是否已经完成'), required=False, default=False)

    @notcheck
    @swagger_auto_schema(query_serializer=CeleryTaskQueryParams)
    @action('get')
    def query(self, request: Request):
        """
        查询 Celery 任务结果
        """
        params = self.CeleryTaskQueryParams(request.query_params).params_data

        task_result = TaskResult.objects.filter(task_id__in=params.task_id)
        serializer = CeleryTaskSerializer(task_result, many=True)
        return JsonResponse(serializer, request=request)

    class AssociatedTaskResultQueryParmas(ParamsSerializer):
        a_id = ListIntField(label=_('任务关联ID'), required=False)
        a_type_name = s.CharField(label=_('任务类型名'), required=False)
        is_done = s.BooleanField(label=_('是否已经完成'), required=False, default=False)

    @notcheck
    @swagger_auto_schema(query_serializer=AssociatedTaskResultQueryParmas, responses=AssociatedTaskResultSer)
    @action('get')
    def query_progress(self, request: Request):
        """
            返回关联任务结果
        """
        params = self.AssociatedTaskResultQueryParmas(request.query_params).params_data
        if params.a_id:
            filter_condition = Q(a_id__in=params.a_id)
        if params.a_type_name:
            filter_condition = filter_condition & Q(a_type_name=params.a_type_name)
        if params.is_done:
            query = AssociatedTaskResult.filter_done_task()
        else:
            query = AssociatedTaskResult.filter_progress_task()
        a_task_results = query.filter(filter_condition)

        serializer = AssociatedTaskResultSer(a_task_results, many=True)
        return JsonResponse(serializer, request=request)

    @notcheck
    @action('get')
    def tasks(self, request: Request):
        """
        查询 Celery 注册的任务
        """
        from celery import current_app
        data = ObjectDict()
        tasks = [dict(id=name, alias=(task.__doc__ or name).strip().split()[0]) for name, task in current_app.tasks.items()
                 if not name.startswith('celery.')]

        data.results = tasks
        return JsonResponse(data, request=request)
