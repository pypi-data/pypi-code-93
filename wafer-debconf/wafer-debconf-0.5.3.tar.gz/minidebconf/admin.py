from django.contrib import admin
from minidebconf.models import Registration


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'involvement', 'gender', 'country')
    list_filter = ('involvement', 'gender', 'days')

admin.site.register(Registration, RegistrationAdmin)
