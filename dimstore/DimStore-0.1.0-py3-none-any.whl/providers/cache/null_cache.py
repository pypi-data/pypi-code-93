"""
    Null cache for configurations without cache provider
"""
from dimsum.providers.cache.cache_registry_base import CacheRegistryBase


class NullCache(CacheRegistryBase):

    def __init__(self):
        pass
    
    def get(self, key, **kwargs):
        return None

    def put(self, key, value, **kwargs):
        return None, False
    
    def stats(self, **kwargs):
        return None
