from django.apps import AppConfig

from framework.translation import _


class CeleryTaskConfig(AppConfig):
    name = 'celery_task'
    verbose_name = _('Celery 任务管理')

    def ready(self):
        from celery_app import app
        app.autodiscover_tasks(force=True)
