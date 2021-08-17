# -*- coding=utf-8 -*-


import redis

from .icache_helper import ICacheHelper


class RedisHelper(ICacheHelper):

    host = '127.0.0.1'
    port = 6379
    db = 0

    def __init__(self, host='127.0.0.1', port=6379, db=0, password=None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password

        pool = redis.ConnectionPool(host=self.host, port=self.port, decode_responses=True)
        self.r = redis.Redis(connection_pool=pool, password=self.password)

    def set(self, key, value):
        self.r.set(key, value)

    def get(self, key):
        return self.r.get(key)

    def delete(self, key):
        self.r.delete(key)

    def hash_mset(self, key, value):
        self.r.hmset(key, value)

    def hash_get_all(self, key):
        return self.r.hgetall(key)
