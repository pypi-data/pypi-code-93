import logging
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, Dict, Any, List, Iterable, Optional, Callable, Awaitable

from convo.core.channels.channel import UserMsg, OutputSocket, InputSocket
from sanic.response import HTTPResponse

log = logging.getLogger(__name__)


class BotRocketChat(OutputSocket):
    @classmethod
    def name(cls) -> Text:
        return "rocketchat"

    def __init__(self, user, password, server_url) -> None:
        from rocketchat_API.rocketchat import RocketChat

        self.rocket = RocketChat(user, password, server_url=server_url)

    @staticmethod
    def _convert_to_rocket_btn(buttons: List[Dict]) -> List[Dict]:
        return [
            {
                "text": b["title"],
                "msg": b["payload"],
                "type": "button",
                "msg_in_chat_window": True,
            }
            for b in buttons
        ]

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        """Send message to output channel"""

        for message_part in text.strip().split("\n\n"):
            self.rocket.chat_post_message(message_part, room_id=recipient_id)

    async def sent_img_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        img_attach = [{"image_url": image, "collapsed": False}]

        return self.rocket.chat_post_message(
            None, room_id=recipient_id, attachments=img_attach
        )

    async def send_attachment(
        self, recipient_id: Text, attachment: Text, **kwargs: Any
    ) -> None:
        return self.rocket.chat_post_message(
            None, room_id=recipient_id, attachments=[attachment]
        )

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        **kwargs: Any,
    ) -> None:
        # implementation is based on
        # https://github.com/RocketChat/Rocket.Chat/pull/11473
        # should work in rocket chat >= 0.69.0
        btn_attach = [{"actions": self._convert_to_rocket_btn(buttons)}]

        return self.rocket.chat_post_message(
            text, room_id=recipient_id, attachments=btn_attach
        )

    async def sent_elmnt(
        self, recipient_id: Text, elements: Iterable[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        return self.rocket.chat_post_message(
            None, room_id=recipient_id, attachments=elements
        )

    async def sent_modified_dict(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        text_detail = json_message.pop("text_detail")

        if json_message.get("channel"):
            if json_message.get("room_id"):
                log.warning(
                    "Only one of `channel` or `room_id` can be passed to a RocketChat "
                    "message post. Defaulting to `channel`."
                )
                del json_message["room_id"]
            return self.rocket.chat_post_message(text_detail, **json_message)
        else:
            json_message.setdefault("room_id", recipient_id)
            return self.rocket.chat_post_message(text_detail, **json_message)


class RocketChatEnter(InputSocket):
    """RocketChat input channel implementation."""

    @classmethod
    def name(cls) -> Text:
        return "rocketchat"

    @classmethod
    def from_cred(cls, credentials: Optional[Dict[Text, Any]]) -> InputSocket:
        if not credentials:
            cls.raise_missing_credentials_exception()

        # pytype: disable=attribute-error
        return cls(
            credentials.get("user"),
            credentials.get("password"),
            credentials.get("server_url"),
        )
        # pytype: enable=attribute-error

    def __init__(self, user: Text, password: Text, server_url: Text) -> None:

        self.user = user
        self.password = password
        self.server_url = server_url

    async def sent_msg(
        self,
        text: Optional[Text],
        sender_name: Optional[Text],
        recipient_id: Optional[Text],
        on_new_message: Callable[[UserMsg], Awaitable[Any]],
        metadata: Optional[Dict],
    ):
        if sender_name != self.user:
            output_channel = self.fetch_output_channel()

            usr_message_detail = UserMsg(
                text,
                output_channel,
                recipient_id,
                input_channel=self.name(),
                metadata=metadata,
            )
            await on_new_message(usr_message_detail)

    def blue_print(
        self, on_new_message: Callable[[UserMsg], Awaitable[Any]]
    ) -> Blueprint:
        rocket_chat_web_hook = Blueprint("rocket_chat_web_hook", __name__)

        @rocket_chat_web_hook.route("/", methods=["GET"])
        async def get_health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @rocket_chat_web_hook.route("/webhook", methods=["GET", "POST"])
        async def webhook(request: Request) -> HTTPResponse:
            output_detail = request.json
            meta_data_detail = self.get_metadata(request)
            if output_detail:
                if "visitor" not in output_detail:
                    sender_detail = output_detail.get("user_name", None)
                    text_detail = output_detail.get("text_detail", None)
                    recieverId = output_detail.get("channel_id", None)
                else:
                    messages_list = output_detail.get("messages", None)
                    text_detail = messages_list[0].get("msg", None)
                    sender_detail = messages_list[0].get("username", None)
                    recieverId = output_detail.get("_id")

                await self.sent_msg(
                    text_detail, sender_detail, recieverId, on_new_message, meta_data_detail
                )

            return response.text("")

        return rocket_chat_web_hook

    def fetch_output_channel(self) -> OutputSocket:
        return BotRocketChat(self.user, self.password, self.server_url)
