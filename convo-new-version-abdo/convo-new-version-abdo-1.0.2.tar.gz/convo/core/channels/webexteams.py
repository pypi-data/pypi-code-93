import logging
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, Optional, Dict, Any, Callable, Awaitable

from sanic.response import HTTPResponse
from webexteamssdk import WebexTeamsAPI, Webhook

from convo.core.channels.channel import InputSocket
from convo.core.channels.channel import UserMsg, OutputSocket

log = logging.getLogger(__name__)


class BotWebexTeams(OutputSocket):
    """A Cisco WebexTeams communication channel."""

    @classmethod
    def name(cls) -> Text:
        return "webexteams"

    def __init__(self, access_token: Optional[Text], room: Optional[Text]) -> None:
        self.room = room
        self.api = WebexTeamsAPI(access_token)

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        reciever = self.room or recipient_id
        for message_part in text.strip().split("\n\n"):
            self.api.messages.create(roomId=reciever, text=message_part)

    async def snd_image_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        reciever = self.room or recipient_id
        return self.api.messages.create(roomId=reciever, files=[image])

    async def send_modified_dict(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        json_message.setdefault("roomId", recipient_id)
        return self.api.messages.create(**json_message)


class WebexTeamsEnter(InputSocket):
    """WebexTeams input channel. Based on the HTTPInputChannel."""

    @classmethod
    def name(cls) -> Text:
        return "webexteams"

    @classmethod
    def from_cred(cls, credentials: Optional[Dict[Text, Any]]) -> InputSocket:
        if not credentials:
            cls.raise_missing_credentials_exception()

        # pytype: disable=attribute-error
        return cls(credentials.get("access_token"), credentials.get("room"))
        # pytype: enable=attribute-error

    def __init__(self, access_token: Text, room: Optional[Text] = None) -> None:
        """Create a Cisco Webex Teams input channel.

        Needs a couple of settings to properly authentication and validate
        messages. Details here https://developer.webex.com/authentication.html

        Args:
            access_token: Cisco WebexTeams bot access token.
            room: the string identifier for a room to which the bot posts
        """
        self.token = access_token
        self.room = room
        self.api = WebexTeamsAPI(access_token)

    async def process_msg(
        self,
        on_new_message: Callable[[UserMsg], Awaitable[Any]],
        text: Optional[Text],
        sender_id: Optional[Text],
        metadata: Optional[Dict],
    ) -> Any:

        try:
            out_socket = self.fetch_output_channel()
            user_message = UserMsg(
                text,
                out_socket,
                sender_id,
                input_channel=self.name(),
                metadata=metadata,
            )
            await on_new_message(user_message)
        except Exception as e:
            log.error(f"Exception when trying to handle message.{e}")
            log.error(str(e), exc_info=True)

    def blue_print(
        self, on_new_message: Callable[[UserMsg], Awaitable[Any]]
    ) -> Blueprint:
        webexteams_web_hooks = Blueprint("webexteams_web_hooks", __name__)

        @webexteams_web_hooks.route("/", methods=["GET"])
        async def get_health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @webexteams_web_hooks.route("/webhook", methods=["POST"])
        async def webhook(request: Request) -> HTTPResponse:
            """Respond to inbound webhook HTTP POST from Webex Teams."""

            log.debug("Received webex webhook call")
            # Get the POST data sent from Webex Teams
            dict_data = request.json

            # Create a Webhook object from the JSON data
            web_hook_object = Webhook(dict_data)
            # Get the msg details
            msg = self.api.messages.get(web_hook_object.data.id)

            # This is a VERY IMPORTANT loop prevention control step.
            # If you respond to all messages...  You will respond to the
            # messages that the bot posts and thereby create a loop
            you = self.api.people.me()
            if msg.personId == you.id:
                # Message was sent by me (bot); do not respond.
                return response.text("OK")

            else:
                metadata = self.get_metadata(request)
                await self.process_msg(
                    on_new_message, msg.text, msg.roomId, metadata
                )
                return response.text("")

        return webexteams_web_hooks

    def fetch_output_channel(self) -> OutputSocket:
        return BotWebexTeams(self.token, self.room)
