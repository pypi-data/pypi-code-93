# -*- coding: utf-8 -*-

import time

from django.core.cache import cache


class CACHE_TYPE(object):
    LOG_CACHE = 'LOG_CACHE_KEYS'


def cache_func(cache_key, func, args=(), timeout=0, cache_type_key=CACHE_TYPE.LOG_CACHE):
    # 默认不缓存，直接执行方法返回，不调用缓存模块
    if timeout == 0:
        return func(*args), ""

    result = cache.get(cache_key, None)
    result_cache_time_key = '%s_time' % cache_key  # 设置缓存时间的key
    result_cache_time = ''
    if result == None:
        result = func(*args)
        cache.set(result_cache_time_key, int(time.time()), timeout=timeout)  # 设置缓存时间
        cache.set(cache_key, result, timeout=timeout)
        cache_keys = cache.get(cache_type_key, set())
        cache_keys.add(result_cache_time_key)
        cache_keys.add(cache_key)
        cache.set(cache_type_key, cache_keys)
    else:
        result_cache_time = cache.get(result_cache_time_key, 0)
    return result, result_cache_time


def clear_cache(cache_type_key):
    '''删除缓存
    '''
    cache_keys = cache.get(cache_type_key, set())
    cache_keys.add(cache_type_key)
    cache.delete_many(cache_keys)


class CacheAttribute(object):
    """计算对象属性,并缓存之
    """

    def __init__(self, method, name=None):
        self.method = method
        self.__doc__ = getattr(method, '__doc__')
        self.name = name or method.__name__

    def __get__(self, inst, cls):
        if inst is None:
            return self
        result = self.method(inst)
        setattr(inst, self.name, result)
        return result


class CachedClassAttribute(CacheAttribute):
    """计算类属性,并在类中缓存之
    """

    def __get__(self, inst, cls):
        for sub_cls in cls.__subclasses__():
            # 缓存一次所有的子类属性
            if not hasattr(sub_cls, self.name):
                super(CachedClassAttribute, self).__get__(sub_cls, sub_cls)
        return super(CachedClassAttribute, self).__get__(cls, cls)
