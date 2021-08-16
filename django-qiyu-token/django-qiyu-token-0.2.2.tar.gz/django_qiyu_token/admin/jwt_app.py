from django.contrib import admin

from django_qiyu_token.models import JwtAppModel


@admin.register(JwtAppModel)
class JwtAppAdmin(admin.ModelAdmin):
    list_display = ("app_name", "app_type", "ctime")
    list_display_links = ("app_name", "app_type")
    search_fields = ("app_name",)
    readonly_fields = ("app_key", "app_type")

    def has_change_permission(self, request, obj=None):
        return False
