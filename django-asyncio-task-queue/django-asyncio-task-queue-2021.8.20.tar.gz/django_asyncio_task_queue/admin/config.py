from django.apps import apps
from django.contrib import admin

from ..models import Config
from ..utils import get_models

class ConfigAdmin(admin.ModelAdmin):
    list_display = ['id','app_label','label','db_table','push_limit']
    list_filter = ['app_label',]

    def db_table(self,obj):
        try:
            model = apps.get_model(*obj.label.split('.'))
            return model._meta.db_table
        except Exception:
            pass

    def get_queryset(self, request):
        for model in get_models():
            defaults = dict(app_label=model._meta.app_label)
            Config.objects.get_or_create(defaults,label=model._meta.label)
        return super().get_queryset(request)

admin.site.register(Config, ConfigAdmin)
