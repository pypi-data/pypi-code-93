import asyncio
import logging
from asyncio import Task
from typing import Optional, Any

import aioredis

from komolibs.core.utils.async_utils import safe_ensure_future
from komolibs.logger import KomoLogger

STOPWORD = "STOP"


class Subscriber:
    subscriber_logger: Optional[KomoLogger] = None
    _shared_instance: "Subscriber" = None

    @classmethod
    def get_instance(cls, url: str, channel: str, output: asyncio.Queue) -> "Subscriber":
        if cls._shared_instance is None:
            cls._shared_instance = Subscriber(url=url, channel=channel, stream_output=output)
        return cls._shared_instance

    @classmethod
    def logger(cls) -> KomoLogger:
        if cls.subscriber_logger is None:
            cls.subscriber_logger = logging.getLogger(__name__)
        return cls.subscriber_logger

    def __init__(self, url: str,
                 channel: Optional[str] = "*",
                 stream_output: asyncio.Queue = asyncio.Queue()):
        self._url = url
        self._channel: Optional[str] = channel
        self._redis: Optional[Any] = None
        self._pubsub: Optional[Any] = None
        self._ready: bool = False

        self._subscribe_task: Optional[Task] = None
        self._message_stream: asyncio.Queue = stream_output

    @property
    def ready(self):
        return self._ready

    async def start(self):
        try:
            self._redis = await aioredis.create_redis(self._url)
            res = await self._redis.subscribe(self._channel)
            self._pubsub = res[0]

            self._subscribe_task = safe_ensure_future(self.redis_subscriber_loop())
            self._ready = True
        except Exception as e:
            self._ready = False
            raise e

    async def stop(self):
        self._redis.close()
        await self._redis.wait_closed()
        if self._subscribe_task is not None:
            self._subscribe_task.cancel()
            self._subscribe_task = None

    @property
    def message_stream(self) -> asyncio.Queue:
        return self._message_stream

    async def redis_subscriber_loop(self):
        while True:
            try:
                while await self._pubsub.wait_message():
                    msg = await self._pubsub.get_json()
                    self.message_stream.put_nowait(msg)
            except asyncio.TimeoutError:
                raise
            except Exception:
                raise
            finally:
                await self.stop()
