from datetime import datetime
import logging
import os
import sys
import traceback

from asgiref.sync import sync_to_async
from django.db import models

from .config import Config
from .error import Error
from .log import Log
from .stat import Stat

class AbstractTask(models.Model):

    class Meta:
        abstract = True

    @classmethod
    def init_model(model):
        defaults = {'app_label':model._meta.app_label}
        model.config, created = Config.objects.get_or_create(defaults,label=model._meta.label)

    async def run_task(self):
        raise NotImplementedError

    @classmethod
    def get_queryset(model):
        raise NotImplementedError

    @classmethod
    async def update_queryset(model,queryset):
        raise NotImplementedError

    @classmethod
    async def get_pushed_count(model):
        raise NotImplementedError

    @classmethod
    def get_push_limit(model):
        return model.config.push_limit

    @classmethod
    async def get_push_count(model):
        return model.get_push_limit() - await model.get_pushed_count()

    @classmethod
    async def push_tasks(model,q):
        push_count = await model.get_push_count()
        if push_count>0:
            task_list = await sync_to_async(list)(model.get_queryset()[0:push_count])
            for task in task_list:
                q.put_nowait(task)
            ids = list(map(lambda t:t.id,task_list))
            queryset = model.objects.filter(id__in=ids)
            await model.update_queryset(queryset)

    async def delete_task(self):
        await sync_to_async(type(self).objects.filter(id=self.id).delete)()

    async def update_task(self, **kwargs):
        if 'updated_at' not in kwargs and hasattr(self,'updated_at'):
            kwargs['updated_at'] = datetime.now()
        await sync_to_async(type(self).objects.filter(id=self.id).update)(**kwargs)

    async def log(self, msg):
        await sync_to_async(Log.objects.create)(
            app_label = self._meta.app_label,
            label=self._meta.label,
            task_id=str(self.id),
            msg=msg,
            created_at=datetime.now()
        )

    async def error(self,e):
        logging.error(e)
        await sync_to_async(Error(
            app_label = self._meta.app_label,
            label=self._meta.label,
            task_id=str(self.id),
            exc_type='.'.join(filter(None,[type(e).__module__,type(e).__name__])),
            exc_value=str(e),
            exc_traceback=''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
        ).save)()

    @classmethod
    def refresh_stat(model):
        defaults = dict(
            app_label = model._meta.app_label,
            error_count = Error.objects.filter(label=model._meta.label).count(),
            log_count = Log.objects.filter(label=model._meta.label).count(),
            updated_at = datetime.now()
        )
        Stat.objects.update_or_create(defaults,label=model._meta.label)
