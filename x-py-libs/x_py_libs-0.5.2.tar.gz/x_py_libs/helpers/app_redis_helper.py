# -*- coding=utf-8 -*-

from .redis_helper import RedisHelper

class AppRedisHelper(object):

    redis_helper = None

    key_prefix = ''

    def __init__(self, *args, **kwargs):
        try:
            host = kwargs.get('host')
            password = kwargs.get('password')
            port = kwargs.get('port')

            self.key_prefix = kwargs.get('key_prefix')

            self.redis_helper = RedisHelper(host=host, port=port, password=password)
            
        except Exception:
            pass

        return super().__init__(*args, **kwargs)

    def get_key_prefix(self, key):
        return self.key_prefix + key

    def set(self, key, value):
        try:
            self.redis_helper.set(self.get_key_prefix(key), value)
        except Exception:
            pass

    def get(self, key):
        try:
            return self.redis_helper.get(self.get_key_prefix(key))
        except Exception:
            return None

    def delete(self, key):
        try:
            return self.redis_helper.delete(self.get_key_prefix(key))
        except Exception:
            return None

    def hash_mset(self, key, value):
        try:
            self.redis_helper.hash_mset(self.get_key_prefix(key), value)
        except Exception:
            pass

    def hash_get_all(self, key):
        try:
            return self.redis_helper.hash_get_all(self.get_key_prefix(key))
        except Exception:
            return None
