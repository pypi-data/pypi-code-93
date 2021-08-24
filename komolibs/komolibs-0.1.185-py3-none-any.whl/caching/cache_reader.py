import logging
from typing import Optional

from aioredis import Redis, create_redis

from komolibs.logger import KomoLogger


class CacheReader:
    cache_reader_logger: Optional[KomoLogger] = None
    _shared_instance: "CacheReader" = None

    @classmethod
    def get_instance(cls, url: str, record_key: str) -> "CacheReader":
        if cls._shared_instance is None:
            cls._shared_instance = CacheReader(url=url, record_key=record_key)
        return cls._shared_instance

    @classmethod
    def logger(cls) -> KomoLogger:
        if cls.cache_reader_logger is None:
            cls.cache_reader_logger = logging.getLogger(__name__)
        return cls.cache_reader_logger

    def __init__(self, url: str, record_key: str):
        self._url: str = url
        self._redis: Optional[Redis] = None
        self._record_key = record_key
        self._ready: bool = False

    @property
    def ready(self):
        return self._ready

    async def start(self):
        self._redis = await create_redis(str(self._url))
        self._ready = True

    async def stop(self):
        self.logger().info(f"Stopping cache reader redis connections.")
        self._redis.close()
        await self._redis.wait_closed()
        self.logger().info(f"Finished stopping cache reader redis connection. ")

    async def read(self):
        try:
            return await self._redis.get(self._record_key)
        except Exception as e:
            raise e

