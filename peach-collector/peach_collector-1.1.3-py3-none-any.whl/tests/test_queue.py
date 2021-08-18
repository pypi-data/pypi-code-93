import aioredis
import orjson
import pytest
import os
from aioredis import RedisError
from aioredis.lock import LockError
from httpx import HTTPError, Request
from pytest_httpx import HTTPXMock, to_response

from peach_collector import PeachCollector, PeachCollectorQueue


def redis_url():
    return os.environ.get("REDIS_URL", "redis://localhost")


@pytest.fixture()
async def redis():
    redis = await aioredis.from_url(redis_url(), encoding="utf-8", decode_responses=True)
    await redis.flushall()
    yield redis
    redis.close()


@pytest.fixture()
async def queue(redis):
    collector = PeachCollector("a-site-key", "an-app-id")
    q = PeachCollectorQueue(redis_url(), collector, name="my_q", batch_size=2)
    for i in range(1, 6):
        await q.push_event({"type": "event-type", "foo": i})
    yield q
    q.close_redis_conn()


@pytest.mark.asyncio
async def test_peach_collector_queue_normal(httpx_mock: HTTPXMock, redis, queue):
    # Events are sent in batches
    call_counter = 0

    def response(request, *args, **kwargs):
        nonlocal call_counter
        batches = [[1, 2], [3, 4], [5]]
        sent = orjson.loads(request.read())
        assert [e["foo"] for e in sent["events"]] == batches[call_counter]
        call_counter += 1
        return to_response(json={"ok": 1})

    httpx_mock.add_callback(response)

    await queue.drain()
    assert await redis.lrange("my_key", 0, -1) == []


@pytest.mark.asyncio
async def test_peach_collector_queue_peach_failures(httpx_mock: HTTPXMock, redis, queue):
    # First batch get through to Peach but second blows up, so those and remaining events
    # remain in queue
    call_counter = 0

    def response(request: Request, *args, **kwargs):
        nonlocal call_counter
        call_counter += 1
        if call_counter == 2:
            raise HTTPError("boom")
        return to_response(json={"ok": 1})

    httpx_mock.add_callback(response)

    await queue.drain()
    remaining = [orjson.loads(e) for e in await redis.lrange("my_q", 0, -1)]
    assert [e["foo"] for e in remaining] == [3, 4, 5]


@pytest.mark.asyncio
async def test_peach_collector_queue_redis_lock(queue):
    lock = await queue._acquire_lock()
    another_q = PeachCollectorQueue(redis_url(), queue.collector, name="my_q")
    with pytest.raises(LockError):
        await another_q._acquire_lock()
    await queue._release_lock(lock)
    # Now that lock should be available
    await another_q._acquire_lock()


@pytest.mark.asyncio
async def test_peach_collector_queue_redis_retries(httpx_mock: HTTPXMock, redis, queue):
    # The first redis delete call fails but the retry succeeds
    def response(request: Request, *args, **kwargs):
        return to_response(json={"ok": 1})

    httpx_mock.add_callback(response)

    call_counter = 0

    async def mock(*args, **kwargs):
        nonlocal call_counter
        call_counter += 1
        if call_counter == 1:
            raise RedisError("boom")
        return await original_ltrim(*args, **kwargs)

    original_ltrim = queue.conn.ltrim
    queue.conn.ltrim = mock

    await queue.drain()
    assert call_counter == 2

    remaining = [orjson.loads(e) for e in await redis.lrange("my_q", 0, -1)]
    assert [e["foo"] for e in remaining] == []
