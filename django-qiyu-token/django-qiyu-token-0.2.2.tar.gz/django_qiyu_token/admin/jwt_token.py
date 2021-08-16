from django.contrib import admin

from django_qiyu_token.models import JwtTokenModel


@admin.register(JwtTokenModel)
class JwtTokenAdmin(admin.ModelAdmin):
    list_display = ("jwt_app", "jwt_sub", "jwt_aud", "jwt_exp", "jwt_nbf")
    list_display_links = ("jwt_app", "jwt_sub")
    list_filter = ("jwt_app",)
    autocomplete_fields = ("jwt_app",)
    readonly_fields = ("jwt_nbf", "jwt_token")

    def has_change_permission(self, request, obj=None):
        return False
