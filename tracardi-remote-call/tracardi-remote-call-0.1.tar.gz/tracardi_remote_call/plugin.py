import asyncio
import json
import aiohttp
from datetime import datetime
from aiohttp import ClientConnectorError
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi_remote_call.model.configuration import RemoteCallConfiguration


class RemoteCallAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = RemoteCallConfiguration(**kwargs)

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

    async def run(self, payload):

        try:

            self._validate_key_value(self.config.headers, "Header")
            self._validate_key_value(self.config.cookies, "Cookie")

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:

                payload = json.dumps(payload, default=self._datetime_handler)
                payload = json.loads(payload)

                params = self.config.get_params_as_json(payload)

                async with session.request(
                        method=self.config.method,
                        url=str(self.config.url),
                        headers=self.config.headers,
                        ssl=self.config.sslCheck,
                        **params
                ) as response:
                    # todo add headers and cookies
                    result = {
                        "status": response.status,
                        "content": await response.json()
                    }

                    if response.status in [200, 201, 202, 203]:
                        return Result(port="response", value=result), Result(port="error", value=None)
                    else:
                        return Result(port="response", value=None), Result(port="error", value=result)

        except ClientConnectorError as e:
            return Result(port="response", value=None), Result(port="error", value=str(e))

        except asyncio.exceptions.TimeoutError:
            return Result(port="response", value=None), Result(port="error", value="Remote call timed out.")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi-remote-call.plugin',
            className='RemoteCallAction',
            inputs=['payload'],
            outputs=["response", "error"],
            init={
                "method": "get",
                "url": None,
                "timeout": 30,
                "headers": {},
                "cookies": {},
                "sslCheck": True,
            },
            manual="remote_call_action"
        ),
        metadata=MetaData(
            name='Remote call',
            desc='Sends request to remote API endpoint.',
            type='flowNode',
            width=200,
            height=100,
            icon='cloud',
            group=["Connectors"]
        )
    )
