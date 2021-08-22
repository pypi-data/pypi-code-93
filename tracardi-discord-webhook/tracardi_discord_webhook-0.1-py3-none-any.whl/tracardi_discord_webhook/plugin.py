import asyncio
import aiohttp
from datetime import datetime
from aiohttp import ClientConnectorError
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi_discord_webhook.model.configuration import DiscordWebHookConfiguration


class DiscordWebHookAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = DiscordWebHookConfiguration(**kwargs)

    @staticmethod
    def _datetime_handler(date):
        if isinstance(date, datetime):
            return date.isoformat()
        raise TypeError("Unknown type")

    @staticmethod
    def _validate_key_value(values, label):
        for name, value in values.items():
            if not isinstance(value, str):
                raise ValueError(
                    "{} values must be strings, `{}` given for {} `{}`".format(label, type(value), label.lower(),
                                                                               name))

    async def run(self, message, username):

        try:

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:

                params = {
                    "json": {
                        "content": message,
                        "username": username
                    }
                }

                async with session.request(
                        method="POST",
                        url=str(self.config.url),
                        **params
                ) as response:
                    # todo add headers and cookies
                    result = {
                        "status": response.status
                    }

                    if response.status in [200, 201, 202, 203]:
                        return Result(port="response", value=result), Result(port="error", value=None)
                    else:
                        return Result(port="response", value=None), Result(port="error", value=result)

        except ClientConnectorError as e:
            return Result(port="response", value=None), Result(port="error", value=str(e))

        except asyncio.exceptions.TimeoutError:
            return Result(port="response", value=None), Result(port="error", value="Discord webhook timed out.")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi_discord_webhook.plugin',
            className='DiscordWebHookAction',
            inputs=['message'],
            outputs=["response", "error"],
            init={
                "url": None,
                "timeout": 10
            },
            version="0.1",
            author="Risto Kowaczewski",
            license="MIT",
            manual="discord_webhook_action"
        ),
        metadata=MetaData(
            name='Discord webhook',
            desc='Sends message to discord webhook.',
            type='flowNode',
            width=200,
            height=100,
            icon='discord',
            group=["Connectors"]
        )
    )
