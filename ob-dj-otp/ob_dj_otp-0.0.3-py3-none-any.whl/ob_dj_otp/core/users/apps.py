from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UserConfig(AppConfig):
    name = "ob_dj_otp.core.users"
    verbose_name = _("users")
