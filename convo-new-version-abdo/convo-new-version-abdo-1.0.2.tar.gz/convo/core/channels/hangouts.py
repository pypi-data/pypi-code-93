import logging
from asyncio import CancelledError
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, List, Dict, Any, Optional, Callable, Iterable, Awaitable, Union

from sanic.response import HTTPResponse
from sanic.exceptions import abort
from oauth2client import client
from oauth2client.crypt import AppIdentityError

from convo.core.channels.channel import InputSocket, OutputSocket, UserMsg

log = logging.getLogger(__name__)

CHANNEL_DETAIL = "hangouts"
CRETS_BASE_URI = "https://www.googleapis.com/service_accounts/v1/metadata/x509/chat@system.gserviceaccount.com"


class HangoutsResult(OutputSocket):
    @classmethod
    def name(cls) -> Text:
        return CHANNEL_DETAIL

    def __init__(self) -> None:
        self.messages = {}

    @staticmethod
    def _get_text_card_(message: Dict[Text, Any]) -> Dict:

        get_card = {
            "cards": [
                {
                    "sections": [
                        {"widgets": [{"textParagraph": {"text": message["text"]}}]}
                    ]
                }
            ]
        }
        return get_card

    @staticmethod
    def _get_image_card(image: Text) -> Dict:
        get_card = {
            "cards": [{"sections": [{"widgets": [{"image": {"imageUrl": image}}]}]}]
        }
        return get_card

    @staticmethod
    def _get_text_btn_cards(text: Text, buttons: List) -> Union[Dict, None]:
        hang_outs_btn = []
        for b in buttons:
            try:
                b_txt, b_pl = b["title"], b["payload"]
            except KeyError:
                log.error(
                    "Buttons must be a list of dicts with 'title' and 'payload' as keys"
                )
                return

            hang_outs_btn.append(
                {
                    "textButton": {
                        "text": b_txt,
                        "onClick": {"action": {"actionMethodName": b_pl}},
                    }
                }
            )

        get_card = {
            "cards": [
                {
                    "sections": [
                        {
                            "widgets": [
                                {"textParagraph": {"text": text}},
                                {"buttons": hang_outs_btn},
                            ]
                        }
                    ]
                }
            ]
        }
        return get_card

    @staticmethod
    def _get_combined_cards(c1: Dict, c2: Dict) -> Dict:
        return {"cards": [*c1["cards"], *c2["cards"]]}

    async def _get_persist_msg(self, message: Dict) -> None:
        """Google Hangouts only accepts single dict with single key 'text'
        for simple text messages. All others responses must be sent as cards.

        In case the bot sends multiple messages, all are transformed to either
        cards or text output"""

        # check whether current and previous message will send 'text' or 'card'
        if self.messages.get("text"):
            message_state = "text"
        elif self.messages.get("cards"):
            message_state = "cards"
        else:
            message_state = None

        if message.get("text"):
            new_message = "text"
        elif message.get("cards"):
            new_message = "cards"
        else:
            raise Exception(
                "Your message to Hangouts channel must either contain 'text' or 'cards'!"
            )

        # depending on above outcome, convert messages into same type and combine
        if new_message == message_state == "text":
            # two text messages are simply appended
            new_text_phrase = " ".join([self.messages.get("text", ""), message["text"]])
            new_msg_phrase = {"text": new_text_phrase}

        elif new_message == message_state == "cards":
            # two cards are combined into one
            new_msg_phrase = self._get_combined_cards(self.messages, message)

        elif message_state == "cards" and new_message == "text":
            # if any message is card, turn text message into TextParagraph card
            # and combine cards
            text_card_phrase = self._get_text_card_(message)
            new_msg_phrase = self._get_combined_cards(self.messages, text_card_phrase)

        elif message_state == "text" and new_message == "cards":
            text_card_phrase = self._get_text_card_(self.messages)
            new_msg_phrase = self._get_combined_cards(text_card_phrase, message)

        elif new_message == "text":
            new_msg_phrase = {"text": message.get("text")}
        else:
            new_msg_phrase = message

        self.messages = new_msg_phrase

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:

        await self._get_persist_msg({"text": text})

    async def sent_img_url(self, recipient_id: Text, image: Text, **kwargs) -> None:

        await self._get_persist_msg(self._get_image_card(image))

    async def send_text_with_buttons(
        self, recipient_id: Text, text: Text, buttons: List, **kwargs
    ) -> None:

        await self._get_persist_msg(self._get_text_btn_cards(text, buttons))

    async def send_attachment(
        self, recipient_id: Text, attachment: Text, **kwargs: Any
    ):

        await self.send_text_message(recipient_id, attachment)

    async def sent_elmnts(
        self, recipient_id: Text, elements: Iterable[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        raise NotImplementedError

    async def send_modified_json(
        self, recipient_id: Text, json_message: Dict, **kwargs
    ) -> None:
        """Custom json payload is simply forwarded to Google Hangouts without
        any modifications. Use this for more complex cards, which can be created
        in actions.py."""
        await self._get_persist_msg(json_message)


# Google Hangouts input channel
class HangoutsEnter(InputSocket):
    """
    Channel that uses Google Hangouts Chat API to communicate.
    """

    @classmethod
    def from_cred(cls, credentials: Optional[Dict[Text, Any]]) -> InputSocket:

        if credentials:
            return cls(credentials.get("project_id"))  # pytype: disable=attribute-error

        return cls()

    def __init__(
        self,
        project_id: Optional[Text] = None,
        hangouts_user_added_name_of_intent: Optional[Text] = "/user_added",
        hangouts_room_added_name_of_intent: Optional[Text] = "/room_added",
        hangouts_removed_name_of_intent: Optional[Text] = "/bot_removed",
    ) -> None:

        self.project_id = project_id
        self.hangouts_user_added_name_of_intent = hangouts_user_added_name_of_intent
        self.hangouts_room_added_name_of_intent = hangouts_room_added_name_of_intent
        self.hangouts_user_added_name_of_intent = hangouts_removed_name_of_intent

    @classmethod
    def name(cls) -> Text:
        return CHANNEL_DETAIL

    @staticmethod
    def _extract_sender_detail(req: Request) -> Text:

        if req.json["type"] == "MESSAGE":
            return req.json["message"]["sender"]["displayName"]

        return req.json["user"]["displayName"]

    # noinspection PyMethodMayBeStatic
    def _extract_msg_detail(self, req: Request) -> Text:

        if req.json["type"] == "MESSAGE":
            msg = req.json["msg"]["text"]

        elif req.json["type"] == "CARD_CLICKED":
            msg = req.json["action"]["actionMethodName"]

        elif req.json["type"] == "ADDED_TO_SPACE":
            if self._extract_room_detail(req) and self.hangouts_room_added_name_of_intent:
                msg = self.hangouts_room_added_name_of_intent
            elif not self._extract_room_detail(req) and self.hangouts_user_added_name_of_intent:
                msg = self.hangouts_user_added_name_of_intent

        elif (
            req.json["type"] == "REMOVED_FROM_SPACE"
            and self.hangouts_user_added_name_of_intent
        ):
            msg = self.hangouts_user_added_name_of_intent
        else:
            msg = ""

        return msg

    @staticmethod
    def _extract_room_detail(req: Request) -> Union[Text, None]:

        if req.json["space"]["type"] == "ROOM":
            return req.json["space"]["displayName"]

    def _extract_input_socket_detail(self) -> Text:
        return self.name()

    def _check_hash(self, bot_token: Text) -> None:
        # see https://developers.google.com/hangouts/chat/how-tos/bots-develop#verifying_bot_authenticity
        try:
            token = client.verify_id_token(
                bot_token, self.project_id, cert_uri=CRETS_BASE_URI
            )

            if token["iss"] != "chat@system.gserviceaccount.com":
                abort(401)
        except AppIdentityError:
            abort(401)

    def blue_print(
        self, on_new_message: Callable[[UserMsg], Awaitable[None]]
    ) -> Blueprint:

        custom_webhook = Blueprint("hangouts_webhook", __name__)

        @custom_webhook.route("/", methods=["GET"])
        async def get_health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def recieved(request: Request) -> HTTPResponse:

            if self.project_id:
                hash = request.headers.get("Authorization").replace("Bearer ", "")
                self._check_hash(hash)

            sender_id = self._extract_sender_detail(request)
            room_detail = self._extract_room_detail(request)
            text_detail = self._extract_msg_detail(request)
            if text_detail is None:
                return response.text("OK")
            socket_input = self._extract_input_socket_detail()

            recielver_detail = HangoutsResult()

            try:
                await on_new_message(
                    UserMsg(
                        text_detail,
                        recielver_detail,
                        sender_id,
                        input_channel=socket_input,
                        metadata={"room": room_detail},
                    )
                )
            except CancelledError:
                log.error(
                    "Message handling timed out for " "user message '{}'.".format(text_detail)
                )
            except Exception as e:
                log.exception(
                    f"An exception occurred while handling user message: {e}, text_detail: {text_detail}"
                )

            return response.json(recielver_detail.messages)

        return custom_webhook
