import hashlib
import hmac
import logging
from fbmessenger import MessengerClient
from fbmessenger.attachments import Image
from fbmessenger.elements import Text as FBText
from fbmessenger.quick_replies import QuickReplies, QuickReply
from fbmessenger.sender_actions import SenderAction

import convo.shared.utils.io
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, List, Dict, Any, Callable, Awaitable, Iterable, Optional

from convo.core.channels.channel import UserMsg, OutputSocket, InputSocket
from sanic.response import HTTPResponse

log = logging.getLogger(__name__)


class MessageCarrier:
    """Implement a fbmessenger to parse incoming webhooks and send msgs."""

    @classmethod
    def name(cls) -> Text:
        return "facebook"

    def __init__(
        self,
        page_access_token: Text,
        on_new_message: Callable[[UserMsg], Awaitable[Any]],
    ) -> None:

        self.on_new_message = on_new_message
        self.client = MessengerClient(page_access_token)
        self.last_message: Dict[Text, Any] = {}

    def get_userId(self) -> Text:
        return self.last_message.get("sender", {}).get("id", "")

    @staticmethod
    def _is_audio_msg(message: Dict[Text, Any]) -> bool:
        """Check if the users message is a recorded voice message."""
        return (
            "message" in message
            and "attachments" in message["message"]
            and message["message"]["attachments"][0]["type"] == "audio"
        )

    @staticmethod
    def _is_image_msg(message: Dict[Text, Any]) -> bool:
        """Check if the users message is an image."""
        return (
            "message" in message
            and "attachments" in message["message"]
            and message["message"]["attachments"][0]["type"] == "image"
        )

    @staticmethod
    def _is_video_msg(message: Dict[Text, Any]) -> bool:
        """Check if the users message is a video."""
        return (
            "message" in message
            and "attachments" in message["message"]
            and message["message"]["attachments"][0]["type"] == "video"
        )

    @staticmethod
    def _is_file_msg(message: Dict[Text, Any]) -> bool:
        """Check if the users message is a file."""
        return (
            "message" in message
            and "attachments" in message["message"]
            and message["message"]["attachments"][0]["type"] == "file"
        )

    @staticmethod
    def _is_user_msg(message: Dict[Text, Any]) -> bool:
        """Check if the message is a message from the user"""
        return (
            "message" in message
            and "text" in message["message"]
            and not message["message"].get("is_echo")
        )

    @staticmethod
    def _is_quick_reply_msg(message: Dict[Text, Any]) -> bool:
        """Check if the message is a quick reply message."""
        return (
            message.get("message") is not None
            and message["message"].get("quick_reply") is not None
            and message["message"]["quick_reply"].get("payload")
        )

    async def handled(self, payload: Dict, metadata: Optional[Dict[Text, Any]]) -> None:
        for entry in payload["entry"]:
            for message in entry["messaging"]:
                self.last_message = message
                if message.get("message"):
                    return await self.msg(message, metadata)
                elif message.get("postback"):
                    return await self.post_back(message, metadata)

    async def msg(
        self, message: Dict[Text, Any], metadata: Optional[Dict[Text, Any]]
    ) -> None:
        """Handle an incoming event from the fb webhook."""

        # quick reply and user message both share 'text' attribute
        # so quick reply should be checked first
        print("####################")
        print(message)
        if self._is_quick_reply_msg(message):
            text = message["message"]["quick_reply"]["payload"]
        elif self._is_user_msg(message):
            text = message["message"]["text"]
        elif self._is_audio_msg(message):
            attachment = message["message"]["attachments"][0]
            text = attachment["payload"]["url"]
        elif self._is_image_msg(message):
            attachment = message["message"]["attachments"][0]
            text = attachment["payload"]["url"]
        elif self._is_video_msg(message):
            attachment = message["message"]["attachments"][0]
            text = attachment["payload"]["url"]
        elif self._is_file_msg(message):
            attachment = message["message"]["attachments"][0]
            text = attachment["payload"]["url"]
        else:
            log.warning(
                "Received a message from facebook that we can not "
                f"handle. Msg: {message}"
            )
            return

        await self._handle_user_msg(text, self.get_userId(), metadata)

    async def post_back(
        self, message: Dict[Text, Any], metadata: Optional[Dict[Text, Any]]
    ) -> None:
        """Handle a postback (e.g. quick reply button)."""

        simple_text = message["postback"]["payload"]
        await self._handle_user_msg(simple_text, self.get_userId(), metadata)

    async def _handle_user_msg(
        self, text: Text, sender_id: Text, metadata: Optional[Dict[Text, Any]]
    ) -> None:
        """Pass on the text to the dialogue engine for processing."""

        out_channel = MsgBot(self.client)
        await out_channel.send_action(sender_id, sender_action="mark_seen")

        user_msg = UserMsg(
            text, out_channel, sender_id, input_channel=self.name(), metadata=metadata
        )
        await out_channel.send_action(sender_id, sender_action="typing_on")
        # noinspection PyBroadException
        try:
            await self.on_new_message(user_msg)
        except Exception:
            log.exception(
                "Exception when trying to handle webhook for facebook message."
            )
            pass
        finally:
            await out_channel.send_action(sender_id, sender_action="typing_off")


class MsgBot(OutputSocket):
    """A bot that uses fb-messenger to communicate."""

    @classmethod
    def name(cls) -> Text:
        return "facebook"

    def __init__(self, messenger_client: MessengerClient) -> None:

        self.messenger_client = messenger_client
        super().__init__()

    def sent(self, recipient_id: Text, element: Any) -> None:
        """Sends a message to the recipient using the messenger client."""

        # this is a bit hacky, but the client doesn't have a proper API to
        # send messages but instead expects the incoming sender to be present
        # which we don't have as it is stored in the input channel.
        self.messenger_client.send(element.to_dict(), recipient_id, "RESPONSE")

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        """Send a message through this channel."""

        for message_part in text.strip().split("\n\n"):
            self.sent(recipient_id, FBText(text=message_part))

    async def sent_img_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        """Sends an image. Default will just post the url as a string."""

        self.sent(recipient_id, Image(url=image))

    async def send_action(self, recipient_id: Text, sender_action: Text) -> None:
        """Sends a sender action to facebook (e.g. "typing_on").

        Args:
            recipient_id: recipient
            sender_action: action to send, e.g. "typing_on" or "mark_seen"
        """

        self.messenger_client.send_action(
            SenderAction(sender_action).to_dict(), recipient_id
        )

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        **kwargs: Any,
    ) -> None:
        """Sends buttons to the output."""

        # buttons is a list of tuples: [(option_name,payload)]
        if len(buttons) > 3:
            convo.shared.utils.io.raising_warning(
                "Facebook API currently allows only up to 3 buttons. "
                "If you add more, all will be ignored."
            )
            await self.send_text_message(recipient_id, text, **kwargs)
        else:
            self._add_post_back_info(buttons)

            # Currently there is no predefined way to create a message with
            # buttons in the fbmessenger framework - so we need to create the
            # payload on our own
            payload = {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": text,
                        "buttons": buttons,
                    },
                }
            }
            self.messenger_client.send(payload, recipient_id, "RESPONSE")

    async def sent_fast_reply(
        self,
        recipient_id: Text,
        text: Text,
        fast_reply: List[Dict[Text, Any]],
        **kwargs: Any,
    ) -> None:
        """Sends quick replies to the output."""

        fast_reply = self._convert_quick_reply(fast_reply)
        self.sent(recipient_id, FBText(text=text, quick_replies=fast_reply))

    async def sent_element(
        self, recipient_id: Text, elements: Iterable[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        """Sends elements to the output."""

        for element in elements:
            if "buttons" in element:
                self._add_post_back_info(element["buttons"])

        pay_load_data = {
            "attachment": {
                "type": "template",
                "pay_load_data": {"template_type": "generic", "elements": elements},
            }
        }
        self.messenger_client.send(pay_load_data, recipient_id, "RESPONSE")

    async def sent_custom_json(
        self, reciever_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Sends custom json data to the output."""

        reciever_id = json_message.pop("sender", {}).pop("id", None) or reciever_id

        self.messenger_client.send(json_message, reciever_id, "RESPONSE")

    @staticmethod
    def _add_post_back_info(buttons: List[Dict[Text, Any]]) -> None:
        """Make sure every button has a type. Modifications happen in place."""
        for button in buttons:
            if "type" not in button:
                button["type"] = "postback"

    @staticmethod
    def _convert_quick_reply(quick_replies: List[Dict[Text, Any]]) -> QuickReplies:
        """Convert quick reply dictionary to FB QuickReplies object"""

        fb_fast_reply = []
        for quick_reply in quick_replies:
            try:
                fb_fast_reply.append(
                    QuickReply(
                        title=quick_reply["title"],
                        payload=quick_reply["payload"],
                        content_type=quick_reply.get("content_type"),
                    )
                )
            except KeyError as e:
                raise ValueError(
                    'Facebook quick replies must define a "{}" field.'.format(e.args[0])
                )

        return QuickReplies(quick_replies=fb_fast_reply)


class FBInputs(InputSocket):
    """Facebook input channel implementation. Based on the HTTPInputChannel."""

    @classmethod
    def name(cls) -> Text:
        return "facebook"

    @classmethod
    def from_cred(cls, credentials: Optional[Dict[Text, Any]]) -> InputSocket:
        if not credentials:
            cls.raise_missing_credentials_exception()

        # pytype: disable=attribute-error
        return cls(
            credentials.get("verify"),
            credentials.get("secret"),
            credentials.get("page-access-token"),
        )
        # pytype: enable=attribute-error

    def __init__(self, fb_verify: Text, fb_secret: Text, fb_access_token: Text) -> None:
        """Create a facebook input channel.

        Needs a couple of settings to properly authentication and validate
        messages. Details to setup:

        https://github.com/rehabstudio/fbmessenger#facebook-app-setup

        Args:
            fb_verify: FB Verification string
                (can be chosen by yourself on webhook creation)
            fb_secret: facebook application secret
            fb_access_token: access token to post in the name of the FB page
        """
        self.fb_verify = fb_verify
        self.fb_secret = fb_secret
        self.fb_access_token = fb_access_token

    def blue_print(
        self, on_new_message: Callable[[UserMsg], Awaitable[Any]]
    ) -> Blueprint:

        fb_web_hook = Blueprint("fb_web_hook", __name__)

        # noinspection PyUnusedLocal
        @fb_web_hook.route("/", methods=["GET"])
        async def get_health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @fb_web_hook.route("/webhook", methods=["GET"])
        async def hash_verification(request: Request) -> HTTPResponse:
            if request.args.get("hub.verify_token") == self.fb_verify:
                return response.text(request.args.get("hub.challenge"))
            else:
                log.warning(
                    "Invalid fb verify token! Make sure this matches "
                    "your webhook settings on the facebook app."
                )
                return response.text("failure, invalid token")

        @fb_web_hook.route("/webhook", methods=["POST"])
        async def webhook(request: Request) -> HTTPResponse:
            sign = request.headers.get("X-Hub-Signature") or ""
            if not self.valid_hub_signature(self.fb_secret, request.body, sign):
                log.warning(
                    "Wrong fb secret! Make sure this matches the "
                    "secret in your facebook app settings"
                )
                return response.text("not validated")

            msger = MessageCarrier(self.fb_access_token, on_new_message)

            meta_data = self.get_metadata(request)
            await msger.handled(request.json, meta_data)
            return response.text("success")

        return fb_web_hook

    @staticmethod
    def valid_hub_signature(
        app_secret, request_payload, hub_signature_header
    ) -> bool:
        """Make sure the incoming webhook requests are properly signed.

        Args:
            app_secret: Secret Key for application
            request_payload: request body
            hub_signature_header: X-Hub-Signature header sent with request

        Returns:
            bool: indicated that hub signature is validated
        """

        # noinspection PyBroadException
        try:
            hashcode_method, hub_sign = hub_signature_header.split("=")
        except Exception:
            pass
        else:
            digest_mod = getattr(hashlib, hashcode_method)
            hmac_obj = hmac.new(
                bytearray(app_secret, "utf8"), request_payload, digest_mod
            )
            generated_hash_code = hmac_obj.hexdigest()
            if hub_sign == generated_hash_code:
                return True
        return False

    def fetch_output_channel(self) -> OutputSocket:
        client_detail = MessengerClient(self.fb_access_token)
        return MsgBot(client_detail)
