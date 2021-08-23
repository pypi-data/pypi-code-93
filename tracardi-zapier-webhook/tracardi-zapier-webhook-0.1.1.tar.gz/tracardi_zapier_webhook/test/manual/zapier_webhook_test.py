import asyncio

from tracardi_zapier_webhook.plugin import ZapierWebHookAction


async def main():
    init = {
        "url": "https://hooks.zapier.com/hooks/catch/10556728/b4b22sz/"
    }

    plugin = ZapierWebHookAction(**init)

    payload = {
        "content": "send message\nssdasd",
        "username": "risto"
    }

    results = await plugin.run(payload)
    print(results)


asyncio.run(main())
