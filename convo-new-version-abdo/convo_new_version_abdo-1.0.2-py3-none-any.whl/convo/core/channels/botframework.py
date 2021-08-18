import datetime
import json
import logging
import requests
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, Dict, Any, List, Iterable, Callable, Awaitable, Optional

from convo.core.channels.channel import UserMsg, OutputSocket, InputSocket
from sanic.response import HTTPResponse

log = logging.getLogger(__name__)

URL_MICROSOFT_OAUTH2 = "https://login.microsoftonline.com"

MICROSOFT_OAUTH2_PATH_FLOW = "botframework.com/oauth2/v2.0/token"


class BotFramework(OutputSocket):
    """A Microsoft Bot Framework communication channel."""

    token_expiry_date = datetime.datetime.now()

    headers = None

    @classmethod
    def name(cls) -> Text:
        return "botframework"

    def __init__(
        self,
        app_id: Text,
        app_password: Text,
        conversation: Dict[Text, Any],
        bot: Text,
        services_url: Text,
    ) -> None:

        services_url = (
            f"{services_url}/" if not services_url.endswith("/") else services_url
        )

        self.app_id = app_id
        self.app_password = app_password
        self.conversation = conversation
        self.global_uri = f"{services_url}v3/"
        self.bot = bot

    async def fetch_headers(self) -> Optional[Dict[Text, Any]]:
        if BotFramework.token_expiry_date < datetime.datetime.now():
            uniform_resource_locator = f"{URL_MICROSOFT_OAUTH2}/{MICROSOFT_OAUTH2_PATH_FLOW}"
            permit_type = "client_credentials"
            range = "https://api.botframework.com/.default"
            pay_load = {
                "client_id": self.app_id,
                "client_secret": self.app_password,
                "grant_type": permit_type,
                "scope": range,
            }

            token_response_outcome = requests.post(uniform_resource_locator, data=pay_load)

            if token_response_outcome.ok:
                token_data_set = token_response_outcome.json()
                access_token_key = token_data_set["access_token"]
                token_expiry = token_data_set["expires_in"]

                delta = datetime.timedelta(seconds=int(token_expiry))
                BotFramework.token_expiry_date = datetime.datetime.now() + delta

                BotFramework.headers = {
                    "content-type": "application/json",
                    "Authorization": "Bearer %s" % access_token_key,
                }
                return BotFramework.headers
            else:
                log.error("Could not get BotFramework token")
        else:
            return BotFramework.headers

    def prepare_mesg(
        self, recipient_id: Text, message_data: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        data_set = {
            "type": "message",
            "recipient": {"id": recipient_id},
            "from": self.bot,
            "channelData": {"notification": {"alert": "true"}},
            "text": "",
        }
        data_set.update(message_data)
        return data_set

    async def post(self, message_data: Dict[Text, Any]) -> None:
        post_msg_uri = "{}conversations/{}/activities".format(
            self.global_uri, self.conversation["id"]
        )
        header = await self.fetch_headers()
        post_response = requests.post(
            post_msg_uri, headers=header, data=json.dumps(message_data)
        )

        if not post_response.ok:
            log.error(
                "Error trying to send botframework messge. Response: %s",
                post_response.text,
            )

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        for message_part in text.strip().split("\n\n"):
            text_msg = {"text": message_part}
            msg = self.prepare_mesg(recipient_id, text_msg)
            await self.post(msg)

    async def post_image_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        hero_matter = {
            "contentType": "application/vnd.microsoft.card.hero",
            "content": {"images": [{"url": image}]},
        }

        image_msg = {"attachments": [hero_matter]}
        msg = self.prepare_mesg(recipient_id, image_msg)
        await self.post(msg)

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        **kwargs: Any,
    ) -> None:
        hero_matter = {
            "contentType": "application/vnd.microsoft.card.hero",
            "content": {"subtitle": text, "buttons": buttons},
        }

        buttons_msg = {"attachments": [hero_matter]}
        msg = self.prepare_mesg(recipient_id, buttons_msg)
        await self.post(msg)

    async def post_elements(
        self, recipient_id: Text, elements: Iterable[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        for e in elements:
            message = self.prepare_mesg(recipient_id, e)
            await self.post(message)

    async def post_custom_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        # pytype: disable=attribute-error
        json_message.setdefault("type", "message")
        json_message.setdefault("recipient", {}).setdefault("id", recipient_id)
        json_message.setdefault("from", self.bot)
        json_message.setdefault("channelData", {}).setdefault(
            "notification", {}
        ).setdefault("alert", "true")
        json_message.setdefault("text", "")
        await self.post(json_message)
        # pytype: enable=attribute-error


class BotFrameworkEnter(InputSocket):
    """Bot Framework input channel implementation."""

    @classmethod
    def name(cls) -> Text:
        return "botframework"

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> InputSocket:
        if not credentials:
            cls.raise_missing_credentials_exception()

        # pytype: disable=attribute-error
        return cls(credentials.get("app_id"), credentials.get("app_password"))
        # pytype: enable=attribute-error

    def __init__(self, app_id: Text, app_password: Text) -> None:
        """Create a Bot Framework input channel.

        Args:
            app_id: Bot Framework's API id
            app_password: Bot Framework application secret
        """

        self.app_id = app_id
        self.app_password = app_password

    @staticmethod
    def append_attachments_to_metadata(
        postdata: Dict[Text, Any], meta_data: Optional[Dict[Text, Any]]
    ) -> Optional[Dict[Text, Any]]:
        """Merge the values of `postdata['attachments']` with `metadata`."""

        if postdata.get("attachments"):
            attachment = {"attachments": postdata["attachments"]}
            if meta_data:
                meta_data.update(attachment)
            else:
                meta_data = attachment

        return meta_data

    def blue_print(
        self, on_new_message: Callable[[UserMsg], Awaitable[Any]]
    ) -> Blueprint:

        bot_framework_webhook = Blueprint("botframework_webhook", __name__)

        # noinspection PyUnusedLocal
        @bot_framework_webhook.route("/", methods=["GET"])
        async def robustness(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @bot_framework_webhook.route("/webhook", methods=["POST"])
        async def webhook(request: Request) -> HTTPResponse:
            post_data = request.json
            meta_data = self.get_metadata(request)

            metadata_along_attachment = self.append_attachments_to_metadata(
                post_data, meta_data
            )

            try:
                if post_data["type"] == "message":
                    out_channels = BotFramework(
                        self.app_id,
                        self.app_password,
                        post_data["conversation"],
                        post_data["recipient"],
                        post_data["serviceUrl"],
                    )

                    user_message = UserMsg(
                        text=post_data.get("text", ""),
                        output_channel=out_channels,
                        sender_id=post_data["from"]["id"],
                        input_channel=self.name(),
                        metadata=metadata_along_attachment,
                    )

                    await on_new_message(user_message)
                else:
                    log.info("Not received message type")
            except Exception as e:
                log.error(f"Exception when trying to handle message.{e}")
                log.debug(e, exc_info=True)
                pass

            return response.text("success")

        return bot_framework_webhook
