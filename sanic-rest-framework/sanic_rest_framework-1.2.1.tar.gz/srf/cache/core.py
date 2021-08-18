"""
@Author: WangYuXiang
@E-mile: Hill@3io.cc
@CreateTime: 2021/8/12 15:00
@DependencyLibrary: 无
@MainFunction：无
@FileDoc:
    cache.py
    缓存组件
"""

from threading import Lock
import pickle
from typing import Any

from srf.utils import ObjectDict, run_awaitable
from srf.exceptions import CacheNoFoundEXC
from sanic_plugin_toolkit import SanicPlugin
from importlib import import_module


__all__ = (
    "Cache",
    "srf_cache"
)


CACGE_CONFIG_KEY = "SRF_CACHE"


def import_modul_by_str(module_path: str) -> Any:
    """
    通过字符串导入模块

    :param module_path: 模块地址 app.views.ListAPIView
    :return: 返回模块对象
    :rtype: Any
    """
    module_path_list = module_path.split('.')
    package_name, module_name = module_path_list[-1], module_path_list[:-1]
    module_name = '.'.join(module_name)
    return getattr(import_module(module_name), package_name)


class SingletonMeta(type):
    """元类——有限的单例模式
    当初始化参数包含new=True时，将构造一个新的对象
    """
    __instance = None
    __lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls.__lock:
            new = kwargs.pop('new', None)
            if new is True:
                return super().__call__(*args, **kwargs)
            if not cls.__instance:
                cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


class Cache(SanicPlugin, metaclass=SingletonMeta):
    """基于aredis
    SANCI_REDIS = {
        max_connections:10,
        max_idle_time=0, 
        idle_check_interval=1,
        'default':{
            'host':'127.0.0.1', 
            'port':6379,  
            'db':1, 
            # Options
            'password':'pwd',  
            'ssl':, 
            'encoding':, 
            'minsize':,
            'maxsize':, 
            'timeout':
        }
    }

    """

    def __init__(self, *args, **kwargs):
        self._caches = ObjectDict()
        self._current_cache = None

        self.connections = ObjectDict()
        super(Cache, self).__init__(*args, **kwargs)

    def on_registered(self, context, reg, *args, **kwargs):
        self.init_app(context, *args, **kwargs)

    def get_config(self, app):
        app_config = app.config
        if CACGE_CONFIG_KEY not in app_config:
            raise TypeError("Sanic config not '%s' value" % CACGE_CONFIG_KEY)
        config = app_config.get(CACGE_CONFIG_KEY)
        if not isinstance(config, dict):
            raise TypeError("Sanic config '%s' value must be a dict type" % CACGE_CONFIG_KEY)
        return config

    def init_db(self, app, engines):

        @app.listener('before_server_start')
        async def aredis_configure(_app, loop):
            for name, config in engines.items():
                engine_module = config['engine_module']
                db_config = config['db_config']
                if not engine_module.has_db:
                    self._caches[name] = engine_module()
                    continue
                connection = await engine_module._create_connection(db_config)
                client_name = name.lower()
                self.connections[client_name] = connection
                self._caches[name] = engine_module(connection)
            setattr(_app, 'cache', self)

        @app.listener('after_server_stop')
        async def close_redis(_app, _loop):
            for engine in self.all_caches.values():
                if engine.has_db:
                    await engine._disconnect_connection()

    def init_app(self, context, *args, **kwargs):
        app = context.app
        self.config = self.get_config(app=app)
        engine_list = {}
        for name, config in self.config.items():
            engine_module_path = config.get('engine')
            engine_module = import_modul_by_str(engine_module_path)
            db_config = config.get('db_config')
            engine_list[name] = {
                'engine_module': engine_module,
                'db_config': db_config,
            }

        self.init_db(app, engine_list)

    def __getitem__(self, key):
        return self.select(key)

    def select(self, name):
        if name in self.all_caches:
            cache = self.all_caches[name]
            self._current_cache = cache
            return cache
        raise CacheNoFoundEXC()

    @property
    def current_cache(self):
        if self._current_cache is None:
            self._current_cache = list(self.all_caches.values())[0]
        return self._current_cache

    @property
    def all_caches(self):
        return self._caches


srf_cache = Cache()
