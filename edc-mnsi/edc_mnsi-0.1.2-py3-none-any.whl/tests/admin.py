from django.contrib import admin

from edc_mnsi.admin import MnsiModelAdminMixin

from .models import Mnsi


@admin.register(Mnsi)
class MnsiModelAdmin(MnsiModelAdminMixin, admin.ModelAdmin):
    pass
