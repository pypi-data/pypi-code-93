#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 09:52:32 2021

@author: nattawoot
"""
from collections import namedtuple
import functools
import os
import time as time_
from datetime import datetime, date, time
import sys

import redis
import json

from loguru import logger

            
def dataset_as_namedtuple(data_name, list_of_data, columns):
    Name = namedtuple(data_name, columns)   
    my_set = []
    for t in list_of_data:
        my_set.append(Name(*t))
        
    return my_set


#%% loguru

def logger_wraps(*, entry=True, exit=True, level="DEBUG"):

    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs)
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper


def timeit(func):

    def wrapped(*args, **kwargs):
        start = time_.time()
        result = func(*args, **kwargs)
        end = time_.time()
        logger.debug("Function '{}' executed in {:f} s", func.__name__, end - start)
        return result

    return wrapped

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            ARGS = ('year', 'month', 'day', 'hour', 'minute',
                     'second', 'microsecond')
            return {'__type__': 'datetime',
                    'args': [getattr(obj, a) for a in ARGS]}
        elif isinstance(obj, date):
            ARGS = ('year', 'month', 'day')
            return {'__type__': 'date',
                    'args': [getattr(obj, a) for a in ARGS]}
        elif isinstance(obj, time):
            ARGS = ('hour', 'minute', 'second', 'microsecond')
            return {'__type__': 'time',
                    'args': [getattr(obj, a) for a in ARGS]}
        # elif isinstance(obj, timedelta):
        #     ARGS = ('days', 'seconds', 'microseconds')
        #     return {'__type__': 'timedelta',
        #             'args': [getattr(obj, a) for a in ARGS]}
        # elif isinstance(obj, decimal.Decimal):
        #     return {'__type__': 'decimal.Decimal',
        #             'args': [str(obj),]}
        elif hasattr(obj, '__class__'):         
            return obj.__dict__
        else:
            return super().default(obj)


class EnhancedJSONDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, object_hook=self.object_hook,
                         **kwargs)

    def object_hook(self, d): 
        if '__type__' not in d:
            return d
        o = sys.modules[__name__]
        for e in d['__type__'].split('.'):
            o = getattr(o, e)
        args, kwargs = d.get('args', ()), d.get('kwargs', {})
        return o(*args, **kwargs)

            
            
            


def redis_cache(key, timeout=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            my_redis = redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)       
            try:
                data_str = my_redis.get(key)
                data = json.loads(data_str, cls=EnhancedJSONDecoder)
            except TypeError:
                data = func(*args, **kwargs)
                data_str = json.dumps(data , cls=EnhancedJSONEncoder)
                my_redis.set(key, data_str, 3600*timeout)            
            return data
        wrapper.__wrapped__ = func
        return wrapper
    return decorator
