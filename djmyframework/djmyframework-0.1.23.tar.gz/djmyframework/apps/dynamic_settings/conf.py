# -*- coding: utf-8 -*-
# @Time    : 2021-04-14 18:00
# @Author  : xzr
# @File    : conf
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :
import copy
import json
import logging

import etcd3
from django.conf import empty, LazySettings
from django.utils.encoding import force_str
from etcd3.watch import WatchResponse

from framework.utils import SingleInstance
from framework.utils.cache import CacheAttribute
from framework.utils.signals import add_signal_handler, signal


class DefaultsSettingsLoader(object):
    prefix_key = '/django/settings/'
    config = {}

    def set_prefix_key(self, other_key):
        self.prefix_key = '%s%s/' % (self.prefix_key, other_key)
        return self.prefix_key

    def get_value(self, name, default_value):
        return self.config.get(name, default_value)

    def set_value(self, name, value):
        self.config[name] = value

    def watch_config(self): pass

    def decode_value(self, value):
        return json.loads(value)

    def encode_value(self, value):
        return json.dumps(value)


class RedisSettingsLoader(DefaultsSettingsLoader):
    def __init__(self, **kwargs):
        self.set_prefix_key(kwargs.pop('prefix_key', 'defaults'))
        import redis
        self.redis_cli = redis.StrictRedis.from_url(**kwargs)

    def get_value(self, name, default_value):
        value = self.redis_cli.hget(self.prefix_key, name)
        if value is None:
            value = default_value
            self.set_value(name, value)
        else:
            value = self.decode_value(value)
        return value

    def set_value(self, name, value):
        self.redis_cli.hset(self.prefix_key, name, self.encode_value(value))


class Etcd3SettingsLoader(DefaultsSettingsLoader):

    def __init__(self, **kwargs):
        self.set_prefix_key(kwargs.pop('prefix_key', 'defaults'))
        self.etcd = etcd3.client(**kwargs)
        self.init_config()
        self.watch_id = None

    def watch_config(self):
        self.watch_id = self.etcd.add_watch_prefix_callback(self.prefix_key, self.watch_callback)

        add_signal_handler(signal.SIGTERM, self.cancel)
        add_signal_handler(signal.SIGINT, self.cancel)

    def cancel(self):
        if self.watch_id:
            self.etcd.cancel_watch(self.watch_id)

    def init_config(self):
        for value, metadata in self.etcd.get_prefix(self.prefix_key):
            config_name = self.get_config_name_from_event_key(metadata.key)
            self.config[config_name] = self.decode_value(value)

    def genrate_key(self, name):
        return '%s%s' % (self.prefix_key, name.strip())

    def set_value(self, name, value):
        self.etcd.put(self.genrate_key(name), self.encode_value(value))

    def get_value(self, name, default_value=None):
        value = self.config.get(name, None)
        if value is None:
            value, metadata = self.etcd.get(self.genrate_key(name))
            if metadata:
                value = self.decode_value(value)
            else:
                value = default_value
                self.set_value(name, value)
                self.config[name] = value
        return value

    def watch_callback(self, rsp: etcd3.watch.WatchResponse):
        for event in rsp.events:
            config_name = self.get_config_name_from_event_key(event.key)
            self.config[config_name] = self.decode_value(event.value)

    def get_config_name_from_event_key(self, key):
        name = force_str(key)[len(self.prefix_key):]
        return name


class Settings(LazySettings):
    def __getattr__(self, name):
        """Return the value of a setting and cache it in self.__dict__."""
        if self._wrapped is empty:
            self._setup(name)
        val = getattr(self._wrapped, name)
        if isinstance(val, SettingOptions):
            val.set_name(name)
            val = val.get_value()
        return val

    def merge(self, settings_dict):
        pass


settings = Settings()


def get_settings_loader():
    from . import settings as _settings
    _SETTINGS_LOADER_ETCD = getattr(_settings, 'SETTINGS_LOADER_ETCD', {})
    _SETTINGS_LOADER_REDIS = getattr(_settings, 'SETTINGS_LOADER_REDIS', {})
    if _SETTINGS_LOADER_REDIS:
        return RedisSettingsLoader(**_SETTINGS_LOADER_REDIS)
    if _SETTINGS_LOADER_ETCD:
        return Etcd3SettingsLoader(**_SETTINGS_LOADER_ETCD)
    logging.info('use DefaultsSettingsLoader')
    return DefaultsSettingsLoader()


class SettingOptionsManager(SingleInstance):
    settings_options_map = {}
    loader: DefaultsSettingsLoader = None


    def genrate_options_key(self, options):
        return '%s/%s' % (options.group, options.name)

    def get_value(self, name):
        # 防止 一开始 settings 未初始化
        if self.loader is None:
            return
        options: SettingOptions = self.settings_options_map.get(name, None)
        if options is not None:
            name = self.genrate_options_key(options)
            value = self.loader.get_value(name, options.default_value)
            return value if value is not None else options.default_value

    def set_value(self, name, value):
        options: SettingOptions = self.settings_options_map.get(name, None)
        if options is not None:
            name = self.genrate_options_key(options)
            return self.loader.set_value(name, value)

    def watch_config(self):
        self.loader = get_settings_loader()
        self.loader.watch_config()

    @property
    def group_options_map(self):
        from django.apps import apps, AppConfig

        group_map = {}
        for k, options in self.settings_options_map.items():
            group_name = options.group
            dj_app_config: AppConfig = apps.app_configs.get(group_name, None)
            if dj_app_config:
                group_name = dj_app_config.verbose_name
            group_map.setdefault(group_name, [])
            group_map[options.group].append(options.to_dict())
        return group_map


settings_manager = SettingOptionsManager()


def get_type_name(value):
    from framework.utils import is_valid_datetime
    if is_valid_datetime(value):
        return 'datetime'
    return type(value).__name__


class SettingOptions(object):
    manager = settings_manager

    def __new__(cls, value, *args, **kwargs):
        if kwargs.pop('is_new', True):
            value_type = type(value)
            value_type = int if value_type == bool else value_type  # type 'bool' is not an acceptable base type
            clazz = type(cls.__name__, (cls, value_type), {})
            kwargs['is_new'] = False
            self = clazz.__new__(clazz, value, *args, **kwargs)
            return self
        else:
            return super().__new__(cls, value)

    def __init__(self, default_value, alias='', name=None, group='defaults', choices=None, lazy=None):
        self.alias = alias
        self.type = type(default_value)
        self.lazy = lazy or self.type
        self.default_value = default_value
        self.choices = choices
        self.name = name
        self.group = group
        self.type_name = get_type_name(default_value)
        self._join_to_manager()

    def _join_to_manager(self):
        if self.name is not None:
            self.manager.settings_options_map[self.name] = self

    def set_name(self, name):
        if self.name is None:
            self.name = force_str(name).strip()
            self._join_to_manager()

    def get_value(self):
        if self.name:
            return self.lazy(self.manager.get_value(self.name))

    @property
    def value(self):
        return self.get_value()

    def set_value(self, value):
        return self.manager.set_value(self.name, value)

    def to_dict(self):
        return dict(value=self.value, alias=self.alias, type=self.type_name, choices=self.choices, name=self.name,
                    default_value=self.default_value)

    def __getattr__(self, item):
        return getattr(self.value, item)

    def __getattribute__(self, item):
        type_attributes = super().__getattribute__('type').__dict__
        if item in type_attributes:
            return super().__getattribute__('value').__getattribute__(item)
        else:
            return super().__getattribute__(item)

    def __getstate__(self):
        return self.to_dict()

    def __get__(self, instance, owner):
        return self.value

    def __eq__(self, other):
        return self.value.__eq__(other)

    def __ne__(self, other):
        return self.value.__ne__(other)

    def __reduce__(self):
        return self.value.__reduce__()

    def __copy__(self):
        return copy.copy(self.value)

    def __deepcopy__(self, memo):
        return copy.deepcopy(self.value)

    def __bytes__(self):
        return self.value.__bytes__()

    def __str__(self):
        return self.value.__str__()

    def __repr__(self):
        return self.value.__repr__()

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __bool__(self):
        return bool(self.value)

    def __eq__(self, other):
        return self.value.__eq__(other)

    def __lt__(self, other):
        return self.value.__lt__(other)

    def __gt__(self, other):
        return self.value.__gt__(other)

    def __ne__(self, other):
        return self.value.__ne__(other)

    def __hash__(self):
        return self.value.__hash__()

    def __getitem__(self, key):
        return self.value.__getitem__(key)

    def __setitem__(self, key, value):
        return self.value.__setitem__(key, value)

    def __delitem__(self, key):
        return self.value.__delitem__(key)

    def __iter__(self):
        return self.value.__iter__()

    def __len__(self):
        return self.value.__len__()

    def __contains__(self, other):
        return self.value.__contains__(other)

    def __instancecheck__(self, instance):
        return isinstance(instance, type(self.value))
