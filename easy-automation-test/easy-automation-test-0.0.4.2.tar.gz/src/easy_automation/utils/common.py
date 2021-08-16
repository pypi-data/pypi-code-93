#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/19
import keyword
import os
import time
from collections import abc
from functools import wraps

from .exception import PathFindError

class Singleton(type):

    def __init__(cls, *args, **kwargs):
        cls._instances = {}
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if args[0] not in cls._instances:
            cls._instances[args[0]] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[args[0]]


def singleton(cls):
    _instance = {}

    def inner(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]
    return inner


class FrozenJson:

    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)
        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, mapping):
        self.__data = {}
        for key, val in mapping.items():
            if keyword.iskeyword(key):
                key += '_'
            self.__data[key] = val

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            if name not in self.__data:
                msg = "'{}' object has no attribute '{}'"
                raise AttributeError(msg.format(self.__class__.__name__, name))
            else:
                return FrozenJson(self.__data[name])


def http_retry(retry_times=3):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal retry_times
            while retry_times > 0:
                resp = func(*args, **kwargs)
                if resp.status_code != 201:
                    retry_times -= 1
                    time.sleep(10)
                    continue
                else:
                    break
            return resp

        return wrapper

    return decorator


def find_project_root_dir():
    cur_dir = os.getcwd()
    while True:
        root, _, files = next(os.walk(cur_dir))
        if 'manage.py' in files:
            return root
        else:
            higher_dir = os.path.dirname(cur_dir)
            if higher_dir == cur_dir:
                raise PathFindError
            else:
                cur_dir = higher_dir