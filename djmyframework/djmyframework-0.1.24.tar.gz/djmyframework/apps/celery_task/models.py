import timezone_field
from celery import states, Task
from django_celery_beat.models import PeriodicTask, IntervalSchedule, SolarSchedule,ClockedSchedule,CrontabSchedule
from django_celery_results.models import TaskResult

from framework.models import BaseModel, models, BaseModelMixin
from framework.translation import _
from framework.utils.cache import CacheAttribute
from .apps import CeleryTaskConfig

states.PROGRESS = 'PROGRESS'

class ReturnResultTask(Task):

    @property
    def task_id(self):
        return self.request.id

    def update_state(self, task_id=None, state=None, meta=None, **kwargs):
        """Update task state.

        Arguments:
            task_id (str): Id of the task to update.
                Defaults to the id of the current task.
            state (str): New state.
            meta (Dict): State meta-data.
        """
        if task_id is None:
            task_id = self.request.id
        self.backend.store_result(task_id, meta, state, **kwargs)
        # return TaskResult.objects.filter(task_id=self.task_id).first()


# Create your models here.
def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery_app import app

        insp = app.control.inspect()
        d = insp.stats()
        if not d:
            d = {ERROR_KEY: 'No running Celery workers were found.'}
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = {ERROR_KEY: msg}
    except ImportError as e:
        d = {ERROR_KEY: str(e)}
    return d


class AssociatedTaskResult(BaseModel):
    """关联任务结果"""
    task_result = models.ManyToManyField(TaskResult, verbose_name=_('celert 任务结果集'))
    a_id = models.BigIntegerField(verbose_name=_('关联作业标识'), db_index=True)
    a_type_name = models.CharField(max_length=50, verbose_name=_('关联作业类型'), db_index=True)

    done_status = [states.SUCCESS, states.FAILURE, states.REJECTED, states.REVOKED, states.IGNORED]

    class Meta:
        app_label = CeleryTaskConfig.name

    @classmethod
    def create(cls, *args, **kwargs):
        obj = cls.objects.create(*args, **kwargs)

        return obj

    @classmethod
    def create_for_task(cls, celecry_task: Task, a_id, task_name=''):
        """创建关联任务并设置初始进度"""
        task_name = task_name or getattr(celecry_task.request, 'task')
        a_task_result = AssociatedTaskResult.create(a_type_name=task_name,
                                                    a_id=a_id)
        a_task_result.add_task_result(celecry_task.request.id)
        celecry_task.update_state(state=states.PROGRESS, request=celecry_task.request)

    def task_result_id(self):
        return [t.task_id for t in self.task_result.all()]

    def add_task_result(self, task_id):
        task_result, _ = TaskResult.objects.get_or_create(task_id=task_id)
        self.task_result.add(task_result)
        return task_result

    def add_task_results(self, task_ids):
        for task_id in task_ids:
            self.add_task_result(task_id)

    @CacheAttribute
    def is_all_done(self):
        for t in self.task_result.all():
            if t.status not in self.done_status:
                return False
        return True

    @classmethod
    def filter_done_task(cls):

        return cls.objects.filter(task_result__status__in=cls.done_status).filter(
                task_result__isnull=False).prefetch_related(
                'task_result').distinct()

    @classmethod
    def filter_progress_task(cls):
        """还在执行的任务"""
        # 不能直接使用 cls.prefetch_related_all().exclude(task_result__status__in=cls.done_status)

        # TaskResult.objects.prefetch_related('associatedtaskresult_set').filter(associatedtaskresult__a_id=43)
        return cls.objects.exclude(task_result__status__in=cls.done_status).filter(
                task_result__isnull=False).prefetch_related(
                'task_result').distinct()
