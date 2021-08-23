"""
    cache layer
"""
import uuid
from collections import namedtuple
from dimsum.providers.cache.cache_registry_factory import CacheRegistryFactory
from dimsum.providers.persistor.persistor_factory import PersistorFactory

class Cache():
    def __init__(self, config):
        # init cache layer
        self.config = config
        self.time_threshold = self.config['time_threshold']
        self.cache_registry = CacheRegistryFactory.get_cache_registry(self.config.get('registry'))
        self.cache_persistor = PersistorFactory.get_persistor(self.config.get('storage'))
        if hasattr(self.cache_persistor, 'set_expiration'):
            self.cache_persistor.set_expiration(self.config.get('cache_duration'))

    def get(self, key, **kwargs):
        uid = self.cache_registry.get(key)
        if uid is not None:
            # Go in persistor and return feature csv data dumps
            dumps = self.cache_persistor.read(uid)

            if dumps is None:
                print("> Caching feature to storage and re-registering a reference to registry.")
                self.cache_registry.delete(key)
            else:
                # deserialize feature csv data dumps
                return dumps.decode()
        return None

    def put(self, key, value, **kwargs):
        if 'cache_duration' in self.config:
            kwargs['cache_duration'] = self.config['cache_duration']
        uid = str(uuid.uuid4())
        uid_to_evict, put_successful = self.cache_registry.put(key, uid, **kwargs)
        if put_successful:
            # Add the serialized dataset to the persistor
            if uid_to_evict is not None:
                self.cache_persistor.delete(uid_to_evict)
            dumps = bytearray(value, 'utf-8')
            object_uid = namedtuple('object_uid', ['uid'])
            uid_object = object_uid(uid)    # allows the persistor.write method to call .uid
            self.cache_persistor.write(uid_object, dumps, **kwargs)
        else:
            return None

    def clear(self, verbose=True):
        try:
            cache_registry = self.cache_registry.get_cache_registry()
            for ref in cache_registry.values():
                uid = ref.get('uid')
                self.cache_persistor.delete(uid)
            deleted_count = self.cache_registry.delete(*cache_registry.keys())
            if verbose:
                print(f'> Clearing the cache: {deleted_count} feature(s) affected.')
        except Exception as e:
            print('> Clearing cache registry failed\n ', e)
            raise
