import logging
from typing import Dict, Any

import aioredis
import orjson
from aioredis import RedisError
from aioredis.lock import Lock, LockError
from httpx import HTTPError

from ._collector import PeachCollector
from ._utils import retry_with_backoff, RetryException, retry_secs, check_event

logger = logging.getLogger(__name__)


class PeachCollectorQueue:
    def __init__(
        self,
        redis_url: str,
        collector: PeachCollector = None,
        batch_size=200,
        name="peach_collector",
        lock_ttl_secs=60 * 60 * 24,
        delete_from_redis_retries=10,
        delete_from_redis_retries_exponent=3.0,
    ):
        self.collector = collector
        self.batch_size = batch_size
        self.redis_url = redis_url
        self.conn = aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        self.lock_manager = None
        self.name = name
        self.lock_name = f"{self.name}_lock"
        self.lock_ttl_secs = lock_ttl_secs
        self.delete_from_redis_retries = delete_from_redis_retries
        self.delete_from_redis_retries_exponent = delete_from_redis_retries_exponent
        assert (
            sum(retry_secs(delete_from_redis_retries, delete_from_redis_retries_exponent))
            < self.lock_ttl_secs
        )

    def close_redis_conn(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    async def push_event(self, event: Dict[str, Any]):
        """
        Adds event to queue. Make sure it is json serializable
        """
        await self.conn.rpush(self.name, orjson.dumps(check_event(event)))  # type: ignore

    async def drain(self) -> bool:
        """
        Drains the queue and returns True if we were completely able to send all events to Peach.
        If we're only to send some events so we'll return False. Those events will then be then
        available to send on the next call to drain().

        If we're not able to delete sent events from redis we have a problem that will need to be
        manually resolved before continuing so we don't send duplicates to Peach. This will disable
        the draining from future runs until events and lock are removed manually.

        :returns A boolean indicating if we were able to send all events to Peach
        """
        logger.info("Draining")

        assert self.collector
        lock = await self._acquire_lock()

        events = await self._load_events_from_redis()
        num_sent = await self._send_to_peach(events)
        if num_sent:
            await self._delete_from_redis(num_sent)
        self._log_results(events, num_sent)

        await self._release_lock(lock)

        return num_sent == len(events)

    async def _acquire_lock(self) -> Lock:
        lock = self.conn.lock(self.lock_name, timeout=self.lock_ttl_secs, blocking_timeout=0.1)
        if not await lock.acquire():
            raise LockError("Couldn't get hold of lock")
        return lock

    async def _release_lock(self, lock: Lock):
        return await lock.release()

    async def _load_events_from_redis(self):
        try:
            return await self.conn.lrange(self.name, 0, -1)
        except HTTPError:
            logger.exception("Peach collector raised an HTTP error")
            return []

    async def _send_to_peach(self, events) -> int:
        """
        Send events in batches.  As soon as one calls fails, abort
        :returns An int with how many we've many we've been able to send
        """
        num_sent = 0
        self.collector.events = []
        try:
            # fmt: off
            batches = [
                events[i: i + self.batch_size] for i in range(0, len(events), self.batch_size)
            ]
            # fmt: on
            for batch in batches:
                for event in batch:
                    self.collector.add_event(orjson.loads(event))
                await self.collector.send_events()
                num_sent += len(batch)
        except HTTPError:
            logger.exception("Peach collector raised an HTTP error")
        return num_sent

    async def _delete_from_redis(self, num_sent: int):
        """
        If this fails (after retries) we raise an error which causes drain to crash leaving lock
        in place
        """
        try:

            async def wrap():
                return await self.conn.ltrim(self.name, num_sent, -1)

            await retry_with_backoff(
                wrap,
                self.delete_from_redis_retries,
                self.delete_from_redis_retries_exponent,
                RedisError,
            )

        except RetryException:
            logger.exception(
                f"Failed deleting sent events. You need to manually issue LTRIM 0 {num_sent} before"
                f"deleting {self.lock_name}"
            )

    def _log_results(self, events: list, num_sent: int):
        if not len(events):
            logger.info("No events waiting to be sent to Peach")
            return
        if num_sent == len(events):
            logger.info(f"{num_sent} events sent to Peach")
            return
        if num_sent:
            logger.warning(
                f"We were only able to send {num_sent} out of {len(events)} events to Peach"
            )
            return
        logger.warning(f"We weren't able to send any events to Peach. {len(events)} waiting")
