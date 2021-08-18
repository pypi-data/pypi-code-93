import json

import logging
import requests
from requests import Response
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, Dict, Any, List, Callable, Awaitable, Optional

import convo.shared.utils.common
import convo.shared.utils.io
from convo.shared.constants import CONNECTORS_DOCUMENTS_URL
from convo.core.channels.channel import UserMsg, OutputSocket, InputSocket
from sanic.response import HTTPResponse

from convo.utils import common as common_utils

log = logging.getLogger(__name__)


class BotMattermost(OutputSocket):
    """A Mattermost communication channel"""

    @classmethod
    def name(cls) -> Text:
        return "mattermost"

    @classmethod
    def hash_from_login(cls, url: Text, user: Text, password: Text) -> Optional[Text]:
        """Retrieve access token for mattermost user."""

        detail = {"login_id": user, "password": password}
        s = requests.post(url + "/users/login", data=json.dumps(detail))
        if s.status_code == 200:
            return s.headers["Token"]
        else:
            log.error(f"Failed to login mattermost user {user}. Response: {s}")
            return None

    def __init__(
        self, url: Text, token: Text, bot_channel: Text, webhook_url: Optional[Text]
    ) -> None:
        self.url = url
        self.token = token
        self.bot_channel = bot_channel
        self.webhook_url = webhook_url

        super(BotMattermost, self).__init__()

    def _post_msg_socket(self, channel_id: Text, message: Text):
        return self._payload_data_to_socket(
            {"channel_id": channel_id, "message": message}
        )

    def _payload_data_to_socket(self, data) -> Response:
        """Send a message to a mattermost channel."""

        header_details = {"Authorization": "Bearer " + self.token}
        s = requests.post(self.url + "/posts", headers=header_details, data=json.dumps(data))
        if not s.status_code == 200:
            log.error(
                f"Failed to send message to mattermost channel "
                f"{data.get('channel_id')}. Response: {s}"
            )
        return s

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        for message_part in text.strip().split("\n\n"):
            self._post_msg_socket(self.bot_channel, message_part)

    async def sent_modified_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        json_message.setdefault("channel_id", self.bot_channel)
        json_message.setdefault("message", "")

        self._payload_data_to_socket(json_message)

    async def sent_img_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        """Sends an image."""

        self._payload_data_to_socket(
            {
                "channel_id": self.bot_channel,
                "props": {"attachments": [{"image_url": image}]},
            }
        )

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        **kwargs: Any,
    ) -> None:
        """Sends buttons to the output."""

        # buttons are a list of objects: [(option_name, payload)]
        # See https://docs.mattermost.com/developer/interactive-messages.html#message-buttons

        all_action = [
            {
                "name": button["title"],
                "integration": {
                    "url": self.webhook_url,
                    "context": {"action": button["payload"]},
                },
            }
            for button in buttons
        ]

        all_prop = {"attachments": [{"all_action": all_action}]}

        self._payload_data_to_socket(
            {"channel_id": self.bot_channel, "message": text, "all_prop": all_prop}
        )


class MattermostEnter(InputSocket):
    """Mattermost input channel implemenation."""

    @classmethod
    def name(cls) -> Text:
        return "mattermost"

    @classmethod
    def from_cred(cls, credentials: Optional[Dict[Text, Any]]) -> InputSocket:
        if credentials is None:
            cls.raise_missing_credentials_exception()

        # pytype: disable=attribute-error
        if credentials.get("pw") is not None or credentials.get("user") is not None:
            convo.shared.utils.io.rasing_deprecate_warning(
                "Mattermost recently switched to bot accounts. 'user' and 'pw' "
                "should not be used anymore, you should rather convert your "
                "account to a bot account and use a hash. Password based "
                "authentication will be removed in a future Convo Open Source version.",
                docs=CONNECTORS_DOCUMENTS_URL + "mattermost/",
            )
            hash = BotMattermost.hash_from_login(
                credentials.get("url"), credentials.get("user"), credentials.get("pw")
            )
        else:
            hash = credentials.get("hash")

        return cls(credentials.get("url"), hash, credentials.get("webhook_url"))
        # pytype: enable=attribute-error

    def __init__(self, url: Text, token: Text, webhook_url: Text) -> None:
        """Create a Mattermost input channel.
        Needs a couple of settings to properly authentication and validate
        messages.

        Args:
            url: Your Mattermost team url including /v4 example
                https://mysite.example.com/api/v4
            token: Your mattermost bot token
            webhook_url: The mattermost callback url as specified
                in the outgoing webhooks in mattermost example
                https://mysite.example.com/webhooks/mattermost/webhook
        """
        self.url = url
        self.token = token
        self.webhook_url = webhook_url

    async def msg_with_active_word(
        self,
        on_new_message: Callable[[UserMsg], Awaitable[None]],
        output: Dict[Text, Any],
        metadata: Optional[Dict],
    ) -> None:
        # splitting to get rid of the @botmention
        # trigger we are using for this
        split_msg = output["text"].split(" ", 1)
        if len(split_msg) >= 2:
            msg = split_msg[1]
        else:
            msg = output["text"]

        await self._handled_msg(
            msg, output["user_id"], output["channel_id"], metadata, on_new_message
        )

    async def action_frm_btn(
        self,
        on_new_message: Callable[[UserMsg], Awaitable[None]],
        output: Dict[Text, Any],
        metadata: Optional[Dict],
    ) -> None:
        # get the action_detail, the buttons triggers
        action_detail = output["context"]["action_detail"]

        await self._handled_msg(
            action_detail, output["user_id"], output["channel_id"], metadata, on_new_message
        )

    async def _handled_msg(
        self,
        message: Text,
        sender_id: Text,
        bot_channel: Text,
        metadata: Optional[Dict],
        on_new_message: Callable[[UserMsg], Awaitable[None]],
    ):
        try:
            out_socket_detail = BotMattermost(
                self.url, self.token, bot_channel, self.webhook_url
            )
            user_msg_text = UserMsg(
                message,
                out_socket_detail,
                sender_id,
                input_channel=self.name(),
                metadata=metadata,
            )
            await on_new_message(user_msg_text)
        except Exception as e:
            log.error(f"Exception when trying to handle message.{e}")
            log.debug(e, exc_info=True)

    def blue_print(
        self, on_new_message: Callable[[UserMsg], Awaitable[None]]
    ) -> Blueprint:
        mattermost_webhook = Blueprint("mattermost_webhook", __name__)

        @mattermost_webhook.route("/", methods=["GET"])
        async def get_health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @mattermost_webhook.route("/webhook", methods=["POST"])
        async def webhook(request: Request) -> HTTPResponse:
            output_detail = request.json

            if not output_detail:
                return response.text("")

            meta_data_detail = self.get_metadata(request)
            # handle normal message with trigger_word
            if "trigger_word" in output_detail:
                await self.msg_with_active_word(on_new_message, output_detail, meta_data_detail)

            # handle context actions from buttons
            elif "context" in output_detail:
                await self.action_frm_btn(on_new_message, output_detail, meta_data_detail)

            return response.text("success")

        return mattermost_webhook
