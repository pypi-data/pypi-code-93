import logging
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from typing import Dict, Text, Any, Callable, Awaitable, Optional

from convo.core.channels.channel import InputSocket
from convo.core.channels.channel import UserMsg, OutputSocket

log = logging.getLogger(__name__)


class TWOutput(Client, OutputSocket):
    """Output channel for Twilio"""

    @classmethod
    def name(cls) -> Text:
        return "twilio"

    def __init__(
        self,
        account_sid: Optional[Text],
        auth_token: Optional[Text],
        twilio_number: Optional[Text],
    ) -> None:
        super().__init__(account_sid, auth_token)
        self.twilio_number = twilio_number
        self.send_retry = 0
        self.max_retry = 5

    async def _snd_msg(self, message_data: Dict[Text, Any]):
        msg = None
        try:
            while not msg and self.send_retry < self.max_retry:
                msg = self.messages.create(**message_data)
                self.send_retry += 1
        except TwilioRestException as e:
            log.error("Something went wrong " + repr(e.msg))
        finally:
            self.send_retry = 0

        if not msg and self.send_retry == self.max_retry:
            log.error("Failed to send msg. Max number of retires exceeded.")

        return msg

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        """Sends text message"""

        msg_data = {"to": recipient_id, "from_": self.twilio_number}
        for message_part in text.strip().split("\n\n"):
            msg_data.update({"body": message_part})
            await self._snd_msg(msg_data)

    async def snd_img_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        """Sends an image."""

        message_data = {
            "to": recipient_id,
            "from_": self.twilio_number,
            "media_url": [image],
        }
        await self._snd_msg(message_data)

    async def snd_modified_dict(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Send custom json dict"""

        json_message.setdefault("to", recipient_id)
        if not json_message.get("media_url"):
            json_message.setdefault("body", "")
        if not json_message.get("messaging_service_sid"):
            json_message.setdefault("from_", self.twilio_number)

        await self._snd_msg(json_message)


class TWInput(InputSocket):
    """Twilio input channel"""

    @classmethod
    def name(cls) -> Text:
        return "twilio"

    @classmethod
    def from_cred(cls, credentials: Optional[Dict[Text, Any]]) -> InputSocket:
        if not credentials:
            cls.raise_missing_credentials_exception()

        # pytype: disable=attribute-error
        return cls(
            credentials.get("account_sid"),
            credentials.get("auth_token"),
            credentials.get("twilio_number"),
        )
        # pytype: enable=attribute-error

    def __init__(
        self,
        account_sid: Optional[Text],
        auth_token: Optional[Text],
        twilio_number: Optional[Text],
        debug_mode: bool = True,
    ) -> None:
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.twilio_number = twilio_number
        self.debug_mode = debug_mode

    def blue_print(
        self, on_new_message: Callable[[UserMsg], Awaitable[Any]]
    ) -> Blueprint:
        twilio_webhook = Blueprint("twilio_webhook", __name__)

        @twilio_webhook.route("/", methods=["GET"])
        async def get_health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @twilio_webhook.route("/webhook", methods=["POST"])
        async def msg(request: Request) -> HTTPResponse:
            _sender = request.form.get("From", None)
            text_detail = request.form.get("Body", None)

            out_socket = self.fetch_output_channel()

            if _sender is not None and msg is not None:
                metadata = self.get_metadata(request)
                try:
                    # @ signs get corrupted in SMSes by some carriers
                    text_detail = text_detail.replace("¡", "@")
                    await on_new_message(
                        UserMsg(
                            text_detail,
                            out_socket,
                            _sender,
                            input_channel=self.name(),
                            metadata=metadata,
                        )
                    )
                except Exception as e:
                    log.error(f"Exception when trying to handle msg.{e}")
                    log.debug(e, exc_info=True)
                    if self.debug_mode:
                        raise
                    pass
            else:
                log.debug("Invalid msg")

            return response.text("", status=204)

        return twilio_webhook

    def fetch_output_channel(self) -> OutputSocket:
        return TWOutput(self.account_sid, self.auth_token, self.twilio_number)
