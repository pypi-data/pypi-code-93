from django.conf import settings as django_settings
from django.core.cache import DEFAULT_CACHE_ALIAS

__all__ = ["app_settings"]


defaults = {
    "CACHE_KEY_PREFIX": "dynamic_settings",
    "CACHE_ALIAS": DEFAULT_CACHE_ALIAS,
    "USE_CACHE": True,
    "CACHE_TIMEOUT": 1 * 60 * 60,
}


class AppSettings(object):
    def __init__(self, prefix):
        for key, value in defaults.items():
            dj_setting_key = "%s%s" % (prefix, key)
            self.__setattr__(key, getattr(django_settings, dj_setting_key, value))


app_settings = AppSettings("DYNAMIC_SETTINGS_")
