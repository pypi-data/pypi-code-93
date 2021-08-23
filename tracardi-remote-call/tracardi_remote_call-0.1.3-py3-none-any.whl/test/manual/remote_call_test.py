import asyncio

from tracardi_remote_call.plugin import RemoteCallAction


async def main():
    init = {
        "url": "http://localhost:8686/healthcheck",
        "method": "post",
        "timeout": 1,
        "headers": [
            ("X-AAA", "test")
        ],
        "cookies": {}
    }

    plugin = RemoteCallAction(**init)

    payload = {
        "test": {
            "a": 1,
            "b": [1, 2]
        }
    }

    result = await plugin.run(payload)
    print(result)


asyncio.run(main())
