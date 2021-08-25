import pickle  # nosec: we only pickle Gramex internal objects
import sqlite3


class SQLiteCache():
    '''
    LRU Cache that stores data in a SQLite database. Typical usage::

        >>> store = SQLiteCache(path='path/to/sqlite.db', maxsize=500000)
        >>> value = store.get(key)
        >>> store.set(key, value, expire)

    The `path` in the constructor specifies where to create the SQLite file.

    `maxsize` defines the maximum limit of cache. This will set PRAGMA max_page_count to maxsize /
    page_size (determined from PRAGMA).

    Both Keys and Values are stored as pickle dump.
    # TODO: When the max size is exceeded, implement an LRU logic
    '''
    def __init__(self, path=None, maxsize=None, *args, **kwargs):
        self.store = sqlite3.connect(path, decode_responses=False)
        self.size = 0
        if maxsize:
            if self.currsize > maxsize:
                self.flush()
            self.store.config_set('maxmemory', maxsize)
            self.store.config_set('maxmemory-policy', 'allkeys-lru')  # Approximate LRU cache

    def __getitem__(self, key):
        key = pickle.dumps(key, pickle.HIGHEST_PROTOCOL)
        result = self.store.get(key)
        return None if result is None else pickle.loads(result)     # nosec: frozen input

    def __setitem__(self, key, value, expire=None):
        key = pickle.dumps(key, pickle.HIGHEST_PROTOCOL)
        value = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        if expire and expire <= 0:
            expire = None
        self.store.set(key, value, ex=expire)

    def __len__(self):
        self.size = self.store.dbsize()
        return self.size

    def __iter__(self):
        for key in self.store.scan_iter():
            try:
                yield pickle.loads(key)     # nosec: key is safe
            except pickle.UnpicklingError:
                # If redis already has keys created by other apps, yield them as-is
                yield key

    @property
    def currsize(self):
        '''The current size of cache in bytes'''
        return self.store.info('memory').get('used_memory', None)

    @property
    def maxsize(self):
        '''The max size of cache in bytes'''
        return self.store.info('memory').get('maxmemory', None)

    def get(self, key, *args, **kwargs):
        return self.__getitem__(key)

    def set(self, key, value, expire=None):
        return self.__setitem__(key, value, expire)

    def keys(self):
        return self.store.keys()

    def flush(self):
        '''Delete all keys in the current database'''
        self.store.execute_command('FLUSHDB')
