
from datetime import timedelta


class FakeRedis:
    def __init__(self, host='localhost', port=6379, db=0, password=None,
                decode_responses=False, username=None):
        self.redis_store = {}

    def exists(self, *keys):
        count = 0
        for key in keys:
            if key in self.redis_store:
                count += 1
        return count

    def hget(self, key, field):
        dataset_reference = self.redis_store.get(key)
        if dataset_reference:
            return dataset_reference.get(field)
        return None

    def hset(self, key, field=None, value=None, mapping=None):
        self.redis_store[key] = {}
        if field is None and not mapping:
            raise KeyError("'hset' with no key value pairs")
        if field is not None:
            self.redis_store[key][field] = value
        if mapping:
            for f, v in mapping.items():
                self.redis_store.get(key)[f] = v

    def hincrby(self, key, field, amount = 1):
        dataset_reference = self.redis_store.get(key)
        if dataset_reference:
            dataset_reference[field] = (dataset_reference.get(field) or 0) + amount
        else:
            self.redis_store[key] = {}
            self.redis_store[key][field] = amount

    def flushall(self):
        self.redis_store.clear()

    def dbsize(self):
        return len(self.redis_store)

    def keys(self):
        return self.redis_store.keys()

    def expire(self, key, time):
        if isinstance(time, timedelta):
            time = int(time.total_seconds())
        if isinstance(time, int) and key in self.redis_store:
            return 1
        else:
            return 0

    def delete(self, *keys):
        count = 0
        for key in keys:
            if self.redis_store.pop(key, None) is not None:
                count += 1
        return count

    def hgetall(self, key):
        return self.redis_store.get(key)