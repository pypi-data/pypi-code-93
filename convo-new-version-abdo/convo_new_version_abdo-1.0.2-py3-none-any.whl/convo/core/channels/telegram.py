import logging
from copy import deepcopy
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from telegram import (
    Bot,
    InlineKeyboardButton,
    Update,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from typing import Dict, Text, Any, List, Optional, Callable, Awaitable

from convo.core.channels.channel import InputSocket, UserMsg, OutputSocket
from convo.shared.constants import INTENT_MSG_PREFIX 
from convo.shared.core.constants import  RESTART_USER_INTENT

log = logging.getLogger(__name__)


class TGOutput(Bot, OutputSocket):
    """Output channel for Telegram"""

    # skipcq: PYL-W0236
    @classmethod
    def name(cls) -> Text:
        return "telegram"

    def __init__(self, access_token: Optional[Text]) -> None:
        super().__init__(access_token)

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        for message_part in text.strip().split("\n\n"):
            self.send_message(recipient_id, message_part)

    async def sent_img_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        self.send_photo(recipient_id, image)

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        button_type: Optional[Text] = "inline",
        **kwargs: Any,
    ) -> None:
        """Sends a message with keyboard.

        For more information: https://core.telegram.org/bots#keyboards

        :button_type inline: horizontal inline keyboard

        :button_type vertical: vertical inline keyboard

        :button_type reply: reply keyboard
        """
        if button_type == "inline":
            btn_list = [
                [
                    InlineKeyboardButton(s["title"], callback_data=s["payload"])
                    for s in buttons
                ]
            ]
            respond_markup = InlineKeyboardMarkup(btn_list)

        elif button_type == "vertical":
            btn_list = [
                [InlineKeyboardButton(s["title"], callback_data=s["payload"])]
                for s in buttons
            ]
            respond_markup = InlineKeyboardMarkup(btn_list)

        elif button_type == "reply":
            btn_list = []
            for bttn in buttons:
                if isinstance(bttn, list):
                    btn_list.append([KeyboardButton(s["title"]) for s in bttn])
                else:
                    btn_list.append([KeyboardButton(bttn["title"])])
            respond_markup = ReplyKeyboardMarkup(
                btn_list, resize_keyboard=True, one_time_keyboard=True
            )
        else:
            log.error(
                "Trying to send text with buttons for unknown "
                "button type {}".format(button_type)
            )
            return

        self.send_message(recipient_id, text, reply_markup=respond_markup)

    async def sent_modified_dict(
        self, reciever_id: Text, dict_msg: Dict[Text, Any], **kwargs: Any
    ) -> None:
        dict_msg = deepcopy(dict_msg)

        reciever_id = dict_msg.pop("chat_id", reciever_id)

        sent_func = {
            ("text",): "send_message",
            ("photo",): "send_photo",
            ("audio",): "send_audio",
            ("document",): "send_document",
            ("sticker",): "send_sticker",
            ("video",): "send_video",
            ("video_note",): "send_video_note",
            ("animation",): "send_animation",
            ("voice",): "send_voice",
            ("media",): "send_media_group",
            ("latitude", "longitude", "title", "address"): "send_venue",
            ("latitude", "longitude"): "send_location",
            ("phone_number", "first_name"): "send_contact",
            ("game_short_name",): "send_game",
            ("action",): "send_chat_action",
            (
                "title",
                "decription",
                "payload",
                "provider_token",
                "start_parameter",
                "currency",
                "prices",
            ): "send_invoice",
        }

        for params in sent_func.keys():
            if all(dict_msg.get(p) is not None for p in params):
                arg = [dict_msg.pop(p) for p in params]
                api_call_var = getattr(self, sent_func[params])
                api_call_var(reciever_id, *arg, **dict_msg)


class TGInput(InputSocket):
    """Telegram input channel"""

    @classmethod
    def name(cls) -> Text:
        return "telegram"

    @classmethod
    def from_cred(cls, credentials: Optional[Dict[Text, Any]]) -> InputSocket:
        if not credentials:
            cls.raise_missing_credentials_exception()

        # pytype: disable=attribute-error
        return cls(
            credentials.get("access_token"),
            credentials.get("verify"),
            credentials.get("webhook_url"),
        )
        # pytype: enable=attribute-error

    def __init__(
        self,
        access_token: Optional[Text],
        verify: Optional[Text],
        webhook_url: Optional[Text],
        debug_mode: bool = True,
    ) -> None:
        self.access_token = access_token
        self.verify = verify
        self.webhook_url = webhook_url
        self.debug_mode = debug_mode

    @staticmethod
    def _is_location_type(message) -> bool:
        return message.location is not None

    @staticmethod
    def _is_user_msg_type(message) -> bool:
        return message.text is not None

    @staticmethod
    def _is_btn_type(message) -> bool:
        return message.callback_query is not None

    def blue_print(
        self, on_new_message: Callable[[UserMsg], Awaitable[Any]]
    ) -> Blueprint:
        tg_web_hook = Blueprint("tg_web_hook", __name__)
        out_socket = self.fetch_output_channel()

        @tg_web_hook.route("/", methods=["GET"])
        async def get_health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @tg_web_hook.route("/set_web_hook", methods=["GET", "POST"])
        async def set_web_hook(_: Request) -> HTTPResponse:
            t = out_socket.setWebhook(self.webhook_url)
            if t:
                log.info("Webhook Setup Successful")
                return response.text("Webhook setup successful")
            else:
                log.warning("Webhook Setup Failed")
                return response.text("Invalid webhook")

        @tg_web_hook.route("/webhook", methods=["GET", "POST"])
        async def msg(request: Request) -> Any:
            if request.method == "POST":

                if not out_socket.get_me()["username"] == self.verify:
                    log.debug("Invalid access token, check it matches Telegram")
                    return response.text("failed")

                modified = Update.de_json(request.json, out_socket)
                if self._is_btn_type(modified):
                    message = modified.callback_query.message
                    detail_text = modified.callback_query.data
                else:
                    message = modified.message
                    if self._is_user_msg_type(message):
                        detail_text = message.text.replace("/bot", "")
                    elif self._is_location_type(message):
                        detail_text = '{{"lng":{0}, "lat":{1}}}'.format(
                            message.location.longitude, message.location.latitude
                        )
                    else:
                        return response.text("success")
                sender_id = message.chat.id
                meta_data = self.get_metadata(request)
                try:
                    if detail_text == (INTENT_MSG_PREFIX  + RESTART_USER_INTENT):
                        await on_new_message(
                            UserMsg(
                                detail_text,
                                out_socket,
                                sender_id,
                                input_channel=self.name(),
                                metadata=meta_data,
                            )
                        )
                        await on_new_message(
                            UserMsg(
                                "/start",
                                out_socket,
                                sender_id,
                                input_channel=self.name(),
                                metadata=meta_data,
                            )
                        )
                    else:
                        await on_new_message(
                            UserMsg(
                                detail_text,
                                out_socket,
                                sender_id,
                                input_channel=self.name(),
                                metadata=meta_data,
                            )
                        )
                except Exception as e:
                    log.error(f"Exception when trying to handle message.{e}")
                    log.debug(e, exc_info=True)
                    if self.debug_mode:
                        raise
                    pass

                return response.text("success")

        return tg_web_hook

    def fetch_output_channel(self) -> TGOutput:
        socket = TGOutput(self.access_token)
        socket.setWebhook(self.webhook_url)

        return socket
