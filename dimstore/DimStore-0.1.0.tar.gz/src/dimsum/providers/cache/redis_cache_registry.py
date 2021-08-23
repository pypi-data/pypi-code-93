"""
redis cache registry for computationally expensive features
"""

import inspect
import redis
from collections import OrderedDict
import datetime as dt
from dimsum.utility.cache_functions import create_dataset_reference, stringify_datetime
from dimsum.providers.cache.cache_registry_base import CacheRegistryBase

class RedisCacheRegistry(CacheRegistryBase):
    _UID = 'uid'
    _CACHE_DURATION = 'cache_duration'

    def __init__(self, config):
        self.config = config
        # Redis connection config
        self.redis_conn = self.__get_valid_redis_conn_kwargs__()
        self.client = self.__get_redis_client__()

    def get(self, key, **kwargs):
        try:
            return self.client.hget(key, RedisCacheRegistry._UID)
        except Exception as e:
            print('> cache registry "get" operation failed!\n', e)
            return None

    def put(self, key, uid, **kwargs):
        try:
            if self.client.exists(key) == 0:
                dataset_reference = stringify_datetime(create_dataset_reference(uid, **kwargs))
                self.__set_dataset_reference__(key, dataset_reference)

                cache_duration = kwargs.get(RedisCacheRegistry._CACHE_DURATION)
                if cache_duration:
                    self.client.expire(key, dt.timedelta(days=int(cache_duration)))

                return None, True
        except Exception as e:
                print('> cache registry "put" operation failed!\n', e)
        return None, False

    def delete(self, *keys):
        try:
            return self.client.delete(*keys)
        except Exception as e:
            print('> cache registry "delete" operation failed!\n', e)

    def stats(self, **kwargs):
        pass

    def get_cache_registry(self):
        """
        return the cache registry dictionary
        """
        cache_registry = OrderedDict()
        for key in self.client.keys():
            cache_registry[key] = self.client.hgetall(key)
        return cache_registry

    """
    "   Returns a dictionary of valid keyword arguments that can be passed to the redis.Redis client
    """
    def __get_valid_redis_conn_kwargs__(self):
        valid_keyword_args = [param.name for param in inspect.signature(redis.Redis).parameters.values()
                            if param.kind == param.POSITIONAL_OR_KEYWORD]
        return { kw:self.config[kw] for kw in self.config if kw in valid_keyword_args }

    """
    "   Returns a client interface for the Redis protocol
    """
    def __get_redis_client__(self):
        client = None
        try:
            client = redis.Redis(decode_responses=True, **(self.redis_conn))
        except Exception as e:
            print('> redis client initialization failed! \n', e)
        return client

    """
    "   Saves the dataset reference to the Redis store
    """
    def __set_dataset_reference__(self, key, dataset_reference):
        """
        @param::key: the unique id for the Redis hash that contains the feature reference/information
        @param::dataset_reference: the feature reference/information
        return None
        """
        try:
            if not key:
                raise Exception('> set_dataset_reference: key can not be empty!')
            if dataset_reference == None:
                raise Exception('> set_dataset_reference: dataset_reference can not be None!')
            if not isinstance(key, str):
                raise Exception('> set_dataset_reference: key is not a valid string!')
            if not isinstance(dataset_reference, dict):
                raise Exception('> set_dataset_reference: dataset_reference is not a valid dictionary!')
            self.client.hset(key, mapping=dataset_reference)
        except Exception as e:
            print('"set_dataset_reference" operation failed!\n', e)
            raise
