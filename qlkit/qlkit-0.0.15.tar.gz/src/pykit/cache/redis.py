#!/usr/bin/env python
# -*- coding:utf-8 -*-


class RedisLock(object):
    def __init__(self, redis_connection):
        self.redis_connection = redis_connection

    def lock(self, key, value, expiration):
        pass

    def unlock(self, key):
        """幂等性"""
        pass


class RedisCache(object):
    pass
