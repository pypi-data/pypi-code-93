#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   q.py
@Time    :   2021/08/10 22:29:35
@Author  :   Wei.fu
@Version :   1.0
@Desc    :   异步执行任务
'''

# here put the import lib

import pickle
from redis import Redis


class Queue(object):

    def __init__(self,connect=None, redis_key_name='' ):

        if connect is None:
            self.client = Redis()
        else:
            self.client = connect
        self.key_prefix = 'wq:queue' + redis_key_name

    def add(self, fun: str, **kwargs):
        class_name = ''
        try:
            class_name = fun.__self__.__class__.__name__
            class_kwargs = fun.__self__.__dict__

        except AttributeError:
            class_name = None
            class_kwargs = {}
        pack = fun.__module__
        d = dict(pack=pack,
                 class_kwargs=class_kwargs,
                 class_name=class_name,
                 name=fun.__name__,
                 kwargs=kwargs,
                )
        result = pickle.dumps(d)
        return self.client.rpush(self.key_prefix, result)
