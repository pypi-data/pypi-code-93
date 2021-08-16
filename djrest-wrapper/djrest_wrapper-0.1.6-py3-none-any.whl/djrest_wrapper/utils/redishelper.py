import redis
from django.conf import settings


class Redishelper(object):
    @staticmethod
    def set(key, value):
        server = redis.Redis(connection_pool=settings.REDIS_POOL)
        return server.set(key, value)

    @staticmethod
    def is_exists(key):
        server = redis.Redis(connection_pool=settings.REDIS_POOL)
        return False if server.exists(key) == 0 else True

    @staticmethod
    def delete(key):
        server = redis.Redis(connection_pool=settings.REDIS_POOL)
        return False if server.delete(key) == 0 else True

    @staticmethod
    def set_hash(name, pairs: dict):
        server = redis.Redis(connection_pool=settings.REDIS_POOL)
        for k, v in pairs.items():
            server.hset(name, k, str(v).encode())

    @staticmethod
    def getall_hash(name, server=None):
        if server == None:
            server = redis.Redis(connection_pool=settings.REDIS_POOL)
        data = dict((k.decode(), v.decode())
                    for k, v in server.hgetall(name).items())
        return data

    @staticmethod
    def delete_hash(name):
        server = redis.Redis(connection_pool=settings.REDIS_POOL)
        for key in server.hkeys(name):
            server.hdel(name, key)

    @staticmethod
    def is_exists_hash(name):
        server = redis.Redis(connection_pool=settings.REDIS_POOL)
        pairs = Redishelper.getall_hash(name, server)
        return pairs if pairs != {} else None
