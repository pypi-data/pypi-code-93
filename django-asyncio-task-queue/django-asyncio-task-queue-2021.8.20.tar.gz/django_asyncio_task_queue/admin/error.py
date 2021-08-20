from django.apps import apps
from django.contrib import admin
from django.template.defaultfilters import linebreaksbr
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince

from ..models import Error

class ErrorAdmin(admin.ModelAdmin):
    list_display = ['id','app_label','label','db_table','task_id','exc','traceback','created_at','created_at_timesince']
    list_filter = ['app_label','label','exc_type']

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

    def exc(self, obj):
        return '%s: %s' % (obj.exc_type,obj.exc_value)
    exc.short_description = 'exc'

    def traceback(self,e):
        return mark_safe(linebreaksbr(e.exc_traceback)) if e.exc_traceback else None
    traceback.short_description = 'traceback'

    def created_at_timesince(self, stat):
        if stat.created_at:
            return timesince(stat.created_at).split(',')[0]+' ago'
    created_at_timesince.short_description = ''

admin.site.register(Error, ErrorAdmin)
