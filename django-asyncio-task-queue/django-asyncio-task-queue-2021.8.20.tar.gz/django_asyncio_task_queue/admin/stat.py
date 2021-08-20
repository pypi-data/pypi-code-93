from django.apps import apps
from django.contrib import admin
from django.db import models
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.timesince import timesince

from ..models import Stat
from ..utils import get_models

class StatAdmin(admin.ModelAdmin):
    def db_table(self,obj):
        try:
            model = apps.get_model(*obj.label.split('.'))
            return model._meta.db_table
        except Exception:
            pass

    def get_list_display(self,request):
        fields = ['id','app_label','label','db_table','errors','logs']
        for f in self.model._meta.get_fields():
            if f.name not in fields and f.name not in ['error_count','log_count']:
                fields.append(f.name)
        fields.append('refresh_btn')
        return fields

    def get_list_filter(self,request):
        return ['app_label']+list(map(lambda f:f.name,
            filter(lambda f:isinstance(f,models.BooleanField),self.model._meta.get_fields()
        )))

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def get_search_fields(self,request):
        return [f.name for f in self.model._meta.get_fields()]

    def get_queryset(self, request):
        for model in get_models():
            defaults = dict(app_label=model._meta.app_label)
            Stat.objects.get_or_create(defaults,label=model._meta.label)
        return super().get_queryset(request)

    def get_urls(self):
        return [
            path(
                'django_asyncio_task_queue_stat_refresh/<str:label>',
                self.admin_site.admin_view(self.refresh),
                name='django_asyncio_task_queue_stat_refresh',
            ),
        ] + super().get_urls()

    def has_add_permission(self, request, obj=None):
        return False

    def errors(self, stat):
        if stat.error_count is not None:
            url = reverse('admin:django_asyncio_task_queue_error_changelist')+'?label='+stat.label
            return format_html('<a href="{}">%s</a>' % stat.error_count,url)
    errors.short_description = 'errors'
    errors.allow_tags = True

    def logs(self, stat):
        if stat.log_count is not None:
            url = reverse('admin:django_asyncio_task_queue_log_changelist')+'?label='+stat.label
            return format_html('<a href="{}">%s</a>' % stat.log_count,url,)
    logs.short_description = 'logs'
    logs.allow_tags = True

    def get_refresh_url(self,model):
        return reverse('admin:django_asyncio_task_queue_stat_refresh', args=[model.label])

    def refresh_btn(self, model):
        url = self.get_refresh_url(model)
        return format_html('<a class="button" href="{}">Refresh</a>',url)
    refresh_btn.short_description = ''
    refresh_btn.allow_tags = True

    def refresh(self, request, label):
        model = apps.get_model(*label.split('.'))
        model.refresh_stat()
        url = reverse('admin:django_asyncio_task_queue_stat_changelist')
        return redirect(url)

    def timesince(self,stat):
        if stat.updated_at:
            return timesince(stat.updated_at).split(',')[0]+' ago'
    timesince.short_description = 'updated'

admin.site.register(Stat, StatAdmin)
