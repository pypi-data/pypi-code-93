from django.apps import apps
from django.core.cache import caches
from django.db import transaction
from django.utils.functional import cached_property

from dj_dynamic_settings.app_settings import app_settings
from dj_dynamic_settings.exceptions import SettingNotFoundException
from dj_dynamic_settings.registry import Unset, registry


class Settings(object):
    holder = None

    def __getattr__(self, key):
        if self.holder and (key in self.holder):
            return self.holder[key]

        try:
            return self.get_value(key)
        except SettingNotFoundException:
            raise AttributeError(
                "%s object has no attribute: %s" % (self.__class__.__name__, key)
            )

    def get_value(self, key, check_cache=True):
        if key not in registry:
            raise SettingNotFoundException()

        if app_settings.USE_CACHE and check_cache:
            value = self._get_from_cache(key)
            if not (value is Unset):
                return value

        value = self._get_value(key)
        self._write_to_cache(key, value)
        return value

    def _get_from_cache(self, key):
        cache_key = self._get_cache_key(key)
        value = self.cache.get(cache_key, Unset)
        return value

    def _write_to_cache(self, key, value):
        if not app_settings.USE_CACHE:
            return
        cache_key = self._get_cache_key(key)
        self.cache.set(cache_key, value, timeout=app_settings.CACHE_TIMEOUT)

    def _delete_from_cache(self, key):
        cache_key = self._get_cache_key(key)
        self.cache.delete(cache_key)

    @staticmethod
    def _get_default_value(key):
        setting = registry[key]
        if not (setting.default is Unset):
            return setting.default
        raise SettingNotFoundException()

    def _get_value(self, key):
        if not apps.is_installed("dj_dynamic_settings"):
            return self._get_default_value(key)

        from dj_dynamic_settings.models import Setting

        try:
            setting = Setting.objects.get(key=key, is_active=True)
            return setting.value
        except Setting.DoesNotExist:
            return self._get_default_value(key)

    @cached_property
    def cache(self):
        return caches[app_settings.CACHE_ALIAS]

    @staticmethod
    def _get_cache_key(key):
        return "%s__%s" % (app_settings.CACHE_KEY_PREFIX, key)

    def update(self, setting):
        if setting.is_active:
            self._write_to_cache(setting.key, setting.value)
        else:
            self._delete_from_cache(setting.key)

    def delete(self, key):
        self._delete_from_cache(key)


settings = Settings()


def refresh_settings_cache(sender, instance, *args, **kwargs):
    transaction.on_commit(lambda: settings.update(instance))


def delete_settings_cache(sender, instance, *args, **kwargs):
    transaction.on_commit(lambda: settings.delete(instance.key))
