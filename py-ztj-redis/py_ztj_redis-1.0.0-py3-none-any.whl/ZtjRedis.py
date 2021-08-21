# -*- coding: utf-8 -*-
# Author: Ztj
# Email: ztj1993@gmail.com

import redis


class Redis(object):

    def __init__(self, **kwargs):
        self._pool = None
        self._server = None
        self.options = kwargs

    def pool(self) -> redis.ConnectionPool:
        if self._pool is None:
            self._pool = redis.ConnectionPool(**self.options)
        return self._pool

    def destroy(self):
        self._pool = None
        self._server = None

    def reconnect(self) -> redis.Redis:
        return redis.Redis(connection_pool=self.pool())

    def connect(self) -> redis.Redis:
        if self._server is None:
            self._server = self.reconnect()
        return self._server

    def ping(self):
        try:
            self.connect().ping()
            return True
        except:
            return False
