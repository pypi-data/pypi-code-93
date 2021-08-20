from django.contrib import admin
from django.db import models
from django.utils.timesince import timesince

from ..models import AbstractTask, Stat

class TaskAdmin(admin.ModelAdmin):
    list_display = ['id','priority','is_enabled','is_waiting','is_pushed','created','created_timesince','pushed','pushed_timesince','started','started_timesince','finished','finished_timesince','elapsed',]

    def get_list_display(self,request):
        default_fields = [f.name for f in AbstractTask._meta.get_fields()]
        extra_fields = [f.name for f in self.model._meta.get_fields() if f.name not in default_fields]
        return ['id']+ extra_fields + self.list_display[1:]

    def get_list_filter(self,request):
        boolean_fields = list(filter(
            lambda f:isinstance(f,models.BooleanField),
            self.model._meta.get_fields()
        ))
        return [f.name for f in boolean_fields]

    def get_search_fields(self,request):
        return [f.name for f in self.model._meta.get_fields()]

    def elapsed(self,obj):
        if obj.started_at and obj.finished_at:
            s = str(obj.finished_at - obj.started_at)
            return '.'.join(filter(None,[
                s.split('.')[0].replace('0:00:00','0').replace('0:00:0',''),
                s.split('.')[1][0:2]
            ]))
    elapsed.short_description = 'elapsed'

    def get_date_or_time(self,dt):
        if dt:
            return dt.date() if dt.date()!=dt.date().today() else dt.time()

    def get_timesince(self,dt):
        if dt:
            return timesince(dt).split(',')[0]+' ago'

    def created(self,obj):
        return self.get_date_or_time(obj.created_at)
    created.admin_order_field = 'created_at'
    created.short_description = 'created'

    def created_timesince(self,obj):
        return self.get_timesince(obj.created_at)
    created_timesince.admin_order_field = 'created_at'
    created_timesince.short_description = 'created'

    def pushed(self,obj):
        return self.get_date_or_time(obj.pushed_at)
    pushed.admin_order_field = 'pushed_at'
    pushed.short_description = 'pushed'

    def pushed_timesince(self,obj):
        return self.get_timesince(obj.pushed_at)
    pushed_timesince.admin_order_field = 'pushed_at'
    pushed_timesince.short_description = 'pushed'

    def started(self,obj):
        return self.get_date_or_time(obj.started_at)
    started.admin_order_field = 'started_at'
    started.short_description = 'started'

    def started_timesince(self,obj):
        return self.get_timesince(obj.started_at)
    started_timesince.admin_order_field = 'started_at'
    started_timesince.short_description = 'started'

    def finished(self,obj):
        return self.get_date_or_time(obj.finished_at)
    finished.admin_order_field = 'finished_at'
    finished.short_description = 'finished'

    def finished_timesince(self,obj):
        return self.get_timesince(obj.finished_at)
    finished_timesince.admin_order_field = 'finished_at'
    finished_timesince.short_description = 'finished'

