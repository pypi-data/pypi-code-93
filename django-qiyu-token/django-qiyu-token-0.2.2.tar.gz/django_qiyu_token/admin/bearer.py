from django.contrib import admin

from django_qiyu_token.models import BearerTokenModel


@admin.register(BearerTokenModel)
class BearerTokenAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "token_name",
        "token_type",
        "revoked",
        "expire_time",
        "create_time",
    )
    list_display_links = ("user", "token_name", "token_type")
    list_filter = ("user",)
    autocomplete_fields = ("user",)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return "create_time", "token_value"
        else:
            return "create_time", "user", "token_value"
