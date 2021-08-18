import logging
from typing import Text, Dict, Optional, Callable, Awaitable, Any

from sanic import Blueprint, response
from sanic.request import Request

from convo.core.channels.channel import (
    CollectOutputChannel,
    UserMsg,
    InputSocket,
)
from convo.core.channels.rest import RestApiInput
from convo.utils.endpoints import EndpointConfiguration, ClientResponseError
from sanic.response import HTTPResponse

log = logging.getLogger(__name__)


class Call_back_output(CollectOutputChannel):
    @classmethod
    def name(cls) -> Text:
        return "callback"

    def __init__(self, endpoint: EndpointConfiguration) -> None:

        self.callback_endpoint = endpoint
        super().__init__()

    async def _persist_msg(self, message: Dict[Text, Any]) -> None:
        await super()._persist_message(message)

        try:
            await self.callback_endpoint.request(
                "post", content_type="application/json", json=message
            )
        except ClientResponseError as e:
            log.error(
                "Failed to send output message to callback. "
                "Status: {} Response: {}"
                "".format(e.status, e.text)
            )


class CallbackInsert(RestApiInput):
    """A custom REST http input channel that responds using a callback server.

    Incoming messages are received through a REST interface. Responses
    are sent asynchronously by calling a configured external REST endpoint."""

    @classmethod
    def name(cls) -> Text:
        return "callback"

    @classmethod
    def from_cred(cls, credentials: Optional[Dict[Text, Any]]) -> InputSocket:
        return cls(EndpointConfiguration.from_dict(credentials))

    def __init__(self, endpoint: EndpointConfiguration) -> None:
        self.callback_endpoint = endpoint

    def blue_print(
        self, on_new_message: Callable[[UserMsg], Awaitable[Any]]
    ) -> Blueprint:
        callback_webhook = Blueprint("callback_webhook", __name__)

        @callback_webhook.route("/", methods=["GET"])
        async def robustness(_: Request):
            return response.json({"status": "ok"})

        @callback_webhook.route("/webhook", methods=["POST"])
        async def webhook(request: Request) -> HTTPResponse:
            sender_id = await self._extract_sender_detail(request)
            txt = self._extract_msg_detail(request)

            receiver = self.fetch_output_channel()
            await on_new_message(
                UserMsg(txt, receiver, sender_id, input_channel=self.name())
            )
            return response.text("success")

        return callback_webhook

    def fetch_output_channel(self) -> CollectOutputChannel:
        return Call_back_output(self.callback_endpoint)
