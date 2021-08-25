import pickle
from pathlib import Path
from typing import Dict, Union, Any

import orjson
import rocksdb

from sm.misc.big_dict.inmem import K, V, CacheDictStore


class RocksDBStore(Dict[K, V]):
    def __init__(self, dbfile: Union[Path, str], create_if_missing=True, read_only=False):
        self.db = rocksdb.DB(str(dbfile), rocksdb.Options(create_if_missing=create_if_missing), read_only=read_only)

    def __contains__(self, key):
        return self.db.get(key.encode()) is not None

    def __getitem__(self, key):
        item = self.db.get(key.encode())
        if item is None:
            raise KeyError(key)
        return self.deserialize(item)

    def __setitem__(self, key, value):
        self.db.put(key.encode(), value.encode())

    def __delitem__(self, key):
        self.db.delete(key.encode())

    def __len__(self):
        assert False, "Does not support this operator"

    def get(self, key: str, default=None):
        item = self.db.get(key.encode())
        if item is None:
            return None
        return self.deserialize(item)

    def cache_dict(self) -> 'CacheDictStore[K, V]':
        return CacheDictStore(self)

    def deserialize(self, value):
        return value


class JSONRocksDBStore(RocksDBStore[str, dict]):
    def __setitem__(self, key, value):
        self.db.put(key.encode(), orjson.dumps(value))

    def deserialize(self, value):
        return orjson.loads(value)


class PickleRocksDBStore(RocksDBStore[K, V]):

    def __setitem__(self, key: str, value: Any):
        value = pickle.dumps(value)
        self.db.put(key.encode(), value)

    def deserialize(self, value: bytes):
        return pickle.loads(value)