from django.apps import AppConfig

__all__ = ["DjangoQiyuTokenConfig"]


class DjangoQiyuTokenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_qiyu_token"

    def __init__(self, app_name, app_module):
        super(DjangoQiyuTokenConfig, self).__init__(app_name, app_module)
        self.verbose_name = "认证令牌"
