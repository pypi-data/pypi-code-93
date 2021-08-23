import pytest

from tracardi_remote_call.plugin import RemoteCallAction


@pytest.mark.asyncio
async def test_remote_call_ok():
    init = {
        "url": "http://localhost:8686/healthcheck",
        "method": "post",
        "timeout": 1,
        "headers": [
            ("x-AAA", "test")
        ]
    }

    plugin = RemoteCallAction(**init)

    payload = {
        "test": {
            "a": 1,
            "b": [1, 2]
        }
    }

    results = await plugin.run(payload)
    response, error = results

    assert response.value['status'] == 200
    assert response.value['content'] == payload


@pytest.mark.asyncio
async def test_remote_call_invalid_cookie():
    init = {
        "url": "http://localhost:8686/healthcheck",
        "method": "post",
        "timeout": 1,
        "headers": [
            ("x-AAA", "test")
        ],
        "cookies": {"a": [
            "a"
        ]}
    }

    plugin = RemoteCallAction(**init)

    payload = {
        "test": {
            "a": 1,
            "b": [1, 2]
        }
    }

    try:
        result = await plugin.run(payload)
    except ValueError:
        assert True
