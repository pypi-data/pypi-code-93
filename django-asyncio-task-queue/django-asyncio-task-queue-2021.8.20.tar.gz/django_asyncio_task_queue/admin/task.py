from django.contrib import admin
from django.db import models
from django.utils.timesince import timesince

from ..models import AbstractTask, Stat

class TaskAdmin(admin.ModelAdmin):

    def get_list_display(self,request):
        return [f.name for f in self.model._meta.get_fields()]

    def get_list_filter(self,request):
        boolean_fields = list(filter(
            lambda f:isinstance(f,models.BooleanField),
            self.model._meta.get_fields()
        ))
        return [f.name for f in boolean_fields]

    def get_search_fields(self,request):
        return [f.name for f in self.model._meta.get_fields()]
