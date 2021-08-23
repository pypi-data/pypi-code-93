"""
    Cache Factory class that initializes a NullCache or Cache objects, depending on Config
"""

from dimsum.providers.cache.cache import Cache
from dimsum.providers.cache.null_cache import NullCache


class CacheFactory():

    #cache factory
    @staticmethod
    def get_cache(config):
        if config is None:
            return NullCache()
        # this checks to see if 'cache' is in config, and if so, see if it contains
        # 'time_threshold', 'registry', and 'storage' under it since we need those
        # to instantiate a Cache class
        if set({'time_threshold', 'registry', 'storage'}).issubset(set(config)):
            return Cache(config)
        return NullCache()
