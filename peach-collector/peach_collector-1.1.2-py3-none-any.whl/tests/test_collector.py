import orjson

import pytest
from pytest_httpx import HTTPXMock

from peach_collector import PeachCollector


@pytest.mark.asyncio
async def test_peach_collector(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST")

    collector = PeachCollector("a-site-key", "an-app-id")
    collector.add_event({"type": "event-type", "foo": 666})
    collector.add_event({"type": "event-type", "bar": 777})
    await collector.send_events()

    request = httpx_mock.get_request()
    sent = orjson.loads(request.read())
    assert len(sent["events"]) == 2
    assert sent["events"][0]["foo"] == 666
    assert sent["events"][0]["timestamp"]
    assert sent["events"][0]["pc_client_id"]

    with pytest.raises(AssertionError):
        collector.add_event({"baz": 888})
