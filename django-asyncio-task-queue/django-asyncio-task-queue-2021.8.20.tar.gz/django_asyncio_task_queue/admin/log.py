from datetime import date

from django.apps import apps
from django.contrib import admin
from django.utils.timesince import timesince

from ..models import Log

class LogAdmin(admin.ModelAdmin):
    list_display = ['id','app_label','label','db_table','task_id','msg','created_at_strftime','created_at_timesince']
    list_filter = ['app_label','label',]

    def db_table(self,obj):
        try:
            model = apps.get_model(*obj.label.split('.'))
            return model._meta.db_table
        except Exception:
            pass

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

    def created_at_strftime(self, obj):
        if obj.created_at.date()== date.today():
            return obj.created_at.strftime("%H:%M:%S")
        return obj.created_at.strftime("%Y-%m-%d")
    created_at_strftime.short_description = 'created'

    def created_at_timesince(self, obj):
        if obj.created_at:
            return timesince(obj.created_at).split(',')[0]+' ago'
    created_at_timesince.short_description = ''

admin.site.register(Log, LogAdmin)

