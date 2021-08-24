# -*- coding: utf-8 -*-
# ATENCAO: nao chame este arquivo de redis. Vai entrar em conflito com o modulo redis do sistema

import redis
import os
import zlib

class RedisConnect(object):

    def __init__(self, host=None, port=None, db=None):

        if host is None:
            host = os.environ.get('REDIS_HOST')

        if port is None:
            port = os.environ.get('REDIS_PORT')

        if db is None:
            db = os.environ.get('REDIS_DB')

        self.server = self.set_server(host,port,db)

    @classmethod
    def set_server(self, host, port, db):

        key = '{}:{}/{}'.format(host,port,db)

        if hasattr(self,'pools') is False:
            self.pools = {}
            self.servers = {}

        if key not in self.pools:
            self.pools[key] = redis.ConnectionPool(
                    host=host, port=port, db=db,
                    max_connections=50)

            self.servers[key] = redis.StrictRedis(connection_pool=self.pools[key])

        return self.servers[key]

    #SET VALUES REDIS

    def set(self, key, value):
        return self.server.set(self._generateKey(key), self._zipValue(value))

    def setex(self, key, ttl, value):
        return self.server.setex(self._generateKey(key), ttl, self._zipValue(value))

    def getset(self, key, value):
        result = self.server.getset(self._generateKey(key), self._zipValue(value))
        return self._unzipValue(result)

    def lpush(self, key, value):
        return self.server.lpush(self._generateKey(key), self._zipValue(value))

    #FIM SET VALUES REDIS

    #GET VALUES REDIS

    def get(self, key):
        result = self.server.get(self._generateKey(key))
        return self._unzipValue(result)

    def lpop(self, key):
        result = self.server.lpop(self._generateKey(key))
        return self._unzipValue(result)

    #FIM GET VALUES REDIS

    def expire(self, key, value):
        return self.server.expire(self._generateKey(key), value)

    def exists(self, key):
        return self.server.exists(self._generateKey(key))

    def delete(self, key):
        return self.server.delete(self._generateKey(key))

    def _generateKey(self, key):
        return '{}:001'.format(key)

    #METODOS PRIVADOS
    def _zipValue(self, value):
        if value:
            return zlib.compress(str(value))
        
        return value

    def _unzipValue(self, value):
        try:
            if value:
                return zlib.decompress(value)
        except:
            pass #Se der erro o conteudo nao esta compactado e entao eu retorno o resultado original
            
        return value