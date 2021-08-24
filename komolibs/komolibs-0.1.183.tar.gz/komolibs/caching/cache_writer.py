import asyncio
import logging
from asyncio import Task
from typing import Optional

from aioredis import Redis, create_redis

from komolibs.core.utils.async_utils import safe_ensure_future
from komolibs.logger import KomoLogger


class CacheWriter:
    cache_writer_logger: Optional[KomoLogger] = None
    _shared_instance: "CacheWriter" = None

    @classmethod
    def get_instance(cls, url: str, record_key: str) -> "CacheWriter":
        if cls._shared_instance is None:
            cls._shared_instance = CacheWriter(url=url, record_key=record_key)
        return cls._shared_instance

    @classmethod
    def logger(cls) -> KomoLogger:
        if cls.cache_writer_logger is None:
            cls.cache_writer_logger = logging.getLogger(__name__)
        return cls.cache_writer_logger

    def __init__(self, url: str, record_key: str):
        self._url: str = url
        self._redis: Optional[Redis] = None
        self._record_key = record_key
        self._ready: bool = False

        self._cache_record_task: Optional[Task] = None
        self._cache_queue: asyncio.Queue = asyncio.Queue()

    @property
    def ready(self):
        return self._ready

    @property
    def cache_queue(self) -> asyncio.Queue:
        return self._cache_queue

    async def start(self):
        self._redis = await create_redis(str(self._url))
        self._cache_record_task = safe_ensure_future(self._cache_record_loop())
        self._ready = True

    async def write(self, message: str):
        self._cache_queue.put_nowait(message)

    async def stop(self):
        self.logger().info(f"Stopping cache writer redis connections.")
        self._redis.close()
        await self._redis.wait_closed()
        self.logger().info(f"Finished stopping cache writer redis connection. ")

    async def _cache_record_loop(self):
        self.logger().info(f"Starting cache record loop.")
        while True:
            try:
                record = await self._cache_queue.get()
                await self._redis.set(self._record_key, record)
            except Exception as e:
                raise e
