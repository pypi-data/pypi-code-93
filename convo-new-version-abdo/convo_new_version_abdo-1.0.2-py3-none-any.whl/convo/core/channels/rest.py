import asyncio
import inspect
import json
import logging
from asyncio import Queue, CancelledError
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn

import convo.utils.endpoints
from convo.core.channels.channel import (
    InputSocket,
    CollectOutputChannel,
    UserMsg,
)


log = logging.getLogger(__name__)


class RestApiInput(InputSocket):
    """A custom http input channel.

    This implementation is the basis for a custom implementation of a chat
    frontend. You can customize this to send messages to Convo and
    retrieve responses from the assistant."""

    @classmethod
    def name(cls) -> Text:
        return "rest"

    @staticmethod
    async def on_msg_wrap(
        on_new_message: Callable[[UserMsg], Awaitable[Any]],
        text: Text,
        queue: Queue,
        sender_id: Text,
        input_channel: Text,
        metadata: Optional[Dict[Text, Any]],
    ) -> None:
        fetcher = QueueOutputSocket(queue)

        msg = UserMsg(
            text, fetcher, sender_id, input_channel=input_channel, metadata=metadata
        )
        await on_new_message(msg)

        await queue.put("DONE")  # pytype: disable=bad-return-type

    async def _extract_sender_detail(self, req: Request) -> Optional[Text]:
        return req.json.get("sender", None)

    # noinspection PyMethodMayBeStatic
    def _extract_msg_detail(self, req: Request) -> Optional[Text]:
        return req.json.get("message", None)

    def _extract_input_socket(self, req: Request) -> Text:
        return req.json.get("input_channel") or self.name()

    def buffer_stream_resp(
        self,
        on_new_message: Callable[[UserMsg], Awaitable[None]],
        text: Text,
        sender_id: Text,
        input_channel: Text,
        metadata: Optional[Dict[Text, Any]],
    ) -> Callable[[Any], Awaitable[None]]:
        async def stream(resp: Any) -> None:
            q = Queue()
            job = asyncio.ensure_future(
                self.on_msg_wrap(
                    on_new_message, text, q, sender_id, input_channel, metadata
                )
            )
            output = None  # declare variable up front to avoid pytype error
            while True:
                output = await q.get()
                if output == "DONE":
                    break
                else:
                    await resp.write(json.dumps(output) + "\n")
            await job

        return stream  # pytype: disable=bad-return-type

    def blue_print(
        self, on_new_message: Callable[[UserMsg], Awaitable[None]]
    ) -> Blueprint:
        manual_web_hook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        # noinspection PyUnusedLocal
        @manual_web_hook.route("/", methods=["GET"])
        async def get_health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @manual_web_hook.route("/webhook", methods=["POST"])
        async def recipient(request: Request) -> HTTPResponse:
            sender_id = await self._extract_sender_detail(request)
            text_detail = self._extract_msg_detail(request)
            use_buffer_stream = convo.utils.endpoints.boolean_argument(
                request, "stream", default=False
            )
            input_socket = self._extract_input_socket(request)
            meta_data_detail = self.get_metadata(request)

            if use_buffer_stream:
                return response.stream(
                    self.buffer_stream_resp(
                        on_new_message, text_detail, sender_id, input_socket, meta_data_detail
                    ),
                    content_type="text_detail/event-stream",
                )
            else:
                fetcher = CollectOutputChannel()
                # noinspection PyBroadException
                try:
                    await on_new_message(
                        UserMsg(
                            text_detail,
                            fetcher,
                            sender_id,
                            input_channel=input_socket,
                            metadata=meta_data_detail,
                        )
                    )
                except CancelledError:
                    log.error(
                        f"Message handling timed out for " f"user message '{text_detail}'."
                    )
                except Exception:
                    log.exception(
                        f"An exception occured while handling "
                        f"user message '{text_detail}'."
                    )
                return response.json(fetcher.messages)

        return manual_web_hook


class QueueOutputSocket(CollectOutputChannel):
    """Output channel that collects send messages in a list

    (doesn't send them anywhere, just collects them)."""

    @classmethod
    def name(cls) -> Text:
        return "queue"

    # noinspection PyMissingConstructor
    def __init__(self, message_queue: Optional[Queue] = None) -> None:
        super().__init__()
        self.messages = Queue() if not message_queue else message_queue

    def current_output(self) -> NoReturn:
        raise NotImplementedError("A queue doesn't allow to peek at messages.")

    async def _persist_message(self, message) -> None:
        await self.messages.put(message)  # pytype: disable=bad-return-type
