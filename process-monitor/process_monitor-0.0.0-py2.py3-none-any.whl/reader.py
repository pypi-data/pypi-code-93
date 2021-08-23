import datetime as dt
import json

from .utils import get_elapsed_time


class Reader:
    _redis_hash_map_prefix = "process_monitor"

    def __init__(self, redis_client):
        assert redis_client.connection_pool.connection_kwargs.get('decode_responses'), \
            "Redis instance must have decode_responses=True"
        self.redis_client = redis_client

    def uptime(self, current_datetime, hash_map):
        iso_start_date = hash_map.pop('start_date', None)
        start_date = dt.datetime.fromisoformat(iso_start_date) if iso_start_date else None
        if start_date is None:
            return start_date, "not supported for this processes"

        uptime_str = get_elapsed_time(current_datetime, start_date)
        return iso_start_date, uptime_str

    def _process_info(self, hash_map):
        current_datetime = dt.datetime.now()
        start_date, uptime = self.uptime(current_datetime, hash_map)
        return {
            **hash_map,
            'start_date': start_date,
            'uptime': uptime,
            'last_signal_age': (
                    current_datetime - dt.datetime.fromisoformat(hash_map.get('last_signal'))
            ).total_seconds(),
            'info': json.loads(hash_map['info'])
        }

    def process_info(self, key):
        return self._process_info(self.redis_client.hgetall(key))

    async def async_process_info(self, key):
        return self._process_info(await self.redis_client.hgetall(key))

    def _get_keys(self):
        return self.redis_client.keys("%s_*" % self._redis_hash_map_prefix)

    def read(self):
        keys = self._get_keys()
        return {
            key.replace("%s_" % self._redis_hash_map_prefix, ""): self.process_info(key)
            for key in keys
        }

    async def async_read(self):
        keys = await self._get_keys()
        return {
            key.replace("%s_" % self._redis_hash_map_prefix, ""): await self.async_process_info(key)
            for key in keys
        }
