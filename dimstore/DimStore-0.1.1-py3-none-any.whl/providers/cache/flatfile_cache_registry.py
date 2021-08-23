"""
flat file cache registry for computationally expensive features
"""

from collections import OrderedDict
import pickle as pl
from dimsum.providers.cache.cache_registry_base import CacheRegistryBase
from dimsum.utility.cache_functions import create_dataset_reference, is_expired, remove_all_expired
from dimsum.utility.file_functions import file_exist, read_binary_file, write_binary_file

class FlatFileCacheRegistry(CacheRegistryBase):
    _UID = 'uid'

    def __init__(self, config):
        # User defined config
        self.config = config
        self.path = "%s/%s"%(config['root_dir'], config['folder_name'])
        self.filename = config['file_name']
        self.capacity = config['capacity']

    def get(self, key, **kwargs):
        try:
            cache_registry = self.get_cache_registry()
            dataset_reference = cache_registry.get(key)

            if dataset_reference is None:
                return None

            if is_expired(dataset_reference):
                cache_registry.pop(key)
                self.__save_cache_registry__(cache_registry)
                return None

            cache_registry.move_to_end(key)
            self.__save_cache_registry__(cache_registry)
            return dataset_reference.get(FlatFileCacheRegistry._UID)
        except Exception as e:
            print('> cache registry "get" operation failed!\n', e)
        return None

    def put(self, key, uid, **kwargs):
        if (self.capacity == 0): return

        try:
            cache_registry = self.get_cache_registry()
            dataset_reference = cache_registry.get(key)

            if dataset_reference is None:
                evicted = None
                if len(cache_registry) >= self.capacity:
                    remove_all_expired(cache_registry)
                if len(cache_registry) >= self.capacity:
                    evicted = cache_registry.popitem(last=False)[1]

                cache_registry[key] = create_dataset_reference(uid, **kwargs)
                self.__save_cache_registry__(cache_registry)

                if evicted is not None:
                    return evicted.get(FlatFileCacheRegistry._UID), True
                else:
                    return None, True
        except Exception as e:
            print('> cache registry "put" operation failed!\n', e)
        return None, False

    def delete(self, *keys):
        try:
            cache_registry = self.get_cache_registry()
            count = 0
            for key in keys:
                if cache_registry.pop(key, None) is not None:
                    count += 1

            if count > 0:
                self.__save_cache_registry__(cache_registry)
            return count
        except Exception as e:
            print('> cache registry "delete" operation failed!\n', e)

    def stats(self, **kwargs):
        pass

    """
    "   Read the cache registry dumps and deserialize it
    """
    def get_cache_registry(self):
        """
        return the cache registry dictionary
        """
        cache_registry = OrderedDict()
        if file_exist(self.path, self.filename):
            bytes_obj = read_binary_file(self.path, self.filename)
            cache_registry  = pl.loads(bytes_obj)
        return cache_registry

    """
    "   Serializes the cache registry and saves it to a flat file
    """
    def __save_cache_registry__(self, new_cache_registry):
        """
        @param::new_cache_registry: cache registry object containing collection of cached datasets
        return None
        """
        try:
            if new_cache_registry == None:
                raise Exception('> save_cache_registry: (new)cache_registry can not be None!')
            if not isinstance(new_cache_registry, dict):
                raise Exception('> save_cache_registry: (new)cache_registry is not dictionary type!')

            dumps = pl.dumps(new_cache_registry)
            write_binary_file(self.path, self.filename, dumps)
        except Exception as e:
            print('"save_cache_registry" operation failed!\n', e)
            raise
