"""
    cache registry factory
"""

from dimsum.providers.cache.cache_registry_base import CacheRegistryBase
from dimsum.providers.cache.flatfile_cache_registry import FlatFileCacheRegistry
from dimsum.providers.cache.redis_cache_registry import RedisCacheRegistry
from dimsum.providers.cache.ibm_object_storage_cache_registry import IBMObjectStorageCacheRegistry

class CacheRegistryFactory():

    # cache registry factory
    @staticmethod
    def get_cache_registry(config):
        _TYPE = 'type'
        if not isinstance(config, dict) or config.get(_TYPE) is None:
            raise Exception('> cache registry not created, \'type\' not specified in config')

        type = config.get(_TYPE)
        if type == 'flat_file':
            return FlatFileCacheRegistry(config)
        elif type == 'redis':
            return RedisCacheRegistry(config)
        elif type == 'ibm_object_storage':
            return IBMObjectStorageCacheRegistry(config)
        else:
            raise Exception('> cache registry provider: %s is not supported' % (type))

    # return supported cache registry info
    @staticmethod
    def info():
        return ['flat_file: flat file cache.',
                'redis: redis cache.'
                'ibm_object_storage: IBM object storage cache.']