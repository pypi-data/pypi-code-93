import json
import logging
import re
from typing import Any, Awaitable, Callable, Dict, List, Optional, Text

from convo.core.channels.channel import InputSocket, OutputSocket, UserMsg
import convo.shared.utils.io
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from slack import WebClient

log = logging.getLogger(__name__)


class BotSlack(OutputSocket):
    """A Slack communication channel"""

    @classmethod
    def name(cls) -> Text:
        return "slack"

    def __init__(
        self,
        token: Text,
        slack_channel: Optional[Text] = None,
        thread_id: Optional[Text] = None,
        proxy: Optional[Text] = None,
    ) -> None:

        self.slack_channel = slack_channel
        self.thread_id = thread_id
        self.proxy = proxy
        self.client = WebClient(token, run_async=True, proxy=proxy)
        super().__init__()

    @staticmethod
    def _get_textdetail_from_slack_btn(buttons: List[Dict]) -> Text:
        return "".join([b.get("title", "") for b in buttons])

    async def _post_msg(self, channel, **kwargs: Any):
        if self.thread_id:
            await self.client.chat_postMessage(
                channel=channel, **kwargs, thread_ts=self.thread_id
            )
        else:
            await self.client.chat_postMessage(channel=channel, **kwargs)

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        reciever = self.slack_channel or recipient_id
        for message_part in text.strip().split("\n\n"):
            await self._post_msg(
                channel=reciever, as_user=True, text=message_part, type="mrkdwn"
            )

    async def sent_img_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        reciever = self.slack_channel or recipient_id
        img_area = {"type": "image", "image_url": image, "alt_text": image}

        await self._post_msg(
            channel=reciever, as_user=True, text=image, blocks=[img_area]
        )

    async def send_attachment(
        self, recipient_id: Text, attachment: Dict[Text, Any], **kwargs: Any
    ) -> None:
        reciever = self.slack_channel or recipient_id
        await self._post_msg(
            channel=reciever, as_user=True, attachments=[attachment], **kwargs
        )

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        **kwargs: Any,
    ) -> None:
        reciever = self.slack_channel or recipient_id

        text_area = {"type": "section", "text": {"type": "plain_text", "text": text}}

        if len(buttons) > 5:
            convo.shared.utils.io.raising_warning(
                "Slack API currently allows only up to 5 buttons. "
                "Since you added more than 5, slack will ignore all of them."
            )
            return await self.send_text_message(reciever, text, **kwargs)

        btn_area = {"type": "actions", "elements": []}
        for button in buttons:
            btn_area["elements"].append(
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": button["title"]},
                    "value": button["payload"],
                }
            )

        await self._post_msg(
            channel=reciever,
            as_user=True,
            text=text,
            blocks=[text_area, btn_area],
        )

    async def send_modified_dict(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        socket = json_message.get("socket", self.slack_channel or recipient_id)
        json_message.setdefault("as_user", True)
        await self._post_msg(channel=socket, **json_message)


class SlackEnter(InputSocket):
    """Slack input channel implementation. Based on the HTTPInputChannel."""

    @classmethod
    def name(cls) -> Text:
        return "slack"

    @classmethod
    def from_cred(cls, credentials: Optional[Dict[Text, Any]]) -> InputSocket:
        if not credentials:
            cls.raise_missing_credentials_exception()

        # pytype: disable=attribute-error
        return cls(
            credentials.get("slack_token"),
            credentials.get("slack_channel"),
            credentials.get("proxy"),
            credentials.get("slack_retry_reason_header", "x-slack-retry-reason"),
            credentials.get("slack_retry_number_header", "x-slack-retry-num"),
            credentials.get("errors_ignore_retry", None),
            credentials.get("use_threads", False),
        )
        # pytype: enable=attribute-error

    def __init__(
        self,
        slack_token: Text,
        slack_channel: Optional[Text] = None,
        proxy: Optional[Text] = None,
        slack_retry_reason_header: Optional[Text] = None,
        slack_retry_number_header: Optional[Text] = None,
        errors_ignore_retry: Optional[List[Text]] = None,
        use_threads: Optional[bool] = False,
    ) -> None:
        """Create a Slack input channel.

        Needs a couple of settings to properly authentication and validate
        messages. Details to setup:

        https://github.com/slackapi/python-slackclient

        Args:
            slack_token: Your Slack Authentication token. You can create a
                Slack app and get your Bot User OAuth Access Token
                `here <https://api.slack.com/slack-apps>`_.
            slack_channel: the string identifier for a channel to which
                the bot posts, or channel name (e.g. '#bot-test')
                If not set, messages will be sent back
                to the "App" DM channel of your bot's name.
            proxy: A Proxy Server to route your traffic through
            slack_retry_reason_header: Slack HTTP header name indicating reason that slack send retry request.
            slack_retry_number_header: Slack HTTP header name indicating the attempt number
            errors_ignore_retry: Any error codes given by Slack
                included in this list will be ignored.
                Error codes are listed
                `here <https://api.slack.com/events-api#errors>`_.
            use_threads: If set to True, your bot will send responses in Slack as a threaded message.
                Responses will appear as a normal Slack message if set to False.

        """
        self.slack_token = slack_token
        self.slack_channel = slack_channel
        self.proxy = proxy
        self.errors_ignore_retry = errors_ignore_retry or ("http_timeout",)
        self.retry_reason_header = slack_retry_reason_header
        self.retry_num_header = slack_retry_number_header
        self.use_threads = use_threads

    @staticmethod
    def _is_application_mentioned(slack_event: Dict) -> bool:
        try:
            return slack_event["event"]["type"] == "app_mention"
        except KeyError:
            return False

    @staticmethod
    def _is_direct_msg(slack_event: Dict) -> bool:
        try:
            return slack_event["event"]["channel_type"] == "im"
        except KeyError:
            return False

    @staticmethod
    def _is_user_msg(slack_event: Dict) -> bool:
        return (
            slack_event.get("event") is not None
            and (
                slack_event.get("event", {}).get("type") == "message"
                or slack_event.get("event", {}).get("type") == "app_mention"
            )
            and slack_event.get("event", {}).get("text")
            and not slack_event.get("event", {}).get("bot_id")
        )

    @staticmethod
    def _clean_user_msg(text_detail, uids_to_remove) -> Text:
        """Remove superfluous/wrong/problematic tokens from a message.

        Probably a good starting point for pre-formatting of user-provided text
        to make NLU's life easier in case they go funky to the power of extreme

        In the current state will just drop self-mentions of bot itself

        Args:
            text_detail: raw message as sent from slack
            uids_to_remove: a list of user ids to remove from the content

        Returns:
            str: parsed and cleaned version of the input text
        """

        for uid_to_remove in uids_to_remove:
            # heuristic to format majority cases OK
            # can be adjusted to taste later if needed,
            # but is a good first approximation
            for regex, replaced in [
                (fr"<@{uid_to_remove}>\s", ""),
                (fr"\s<@{uid_to_remove}>", ""),  # a bit arbitrary but probably OK
                (fr"<@{uid_to_remove}>", " "),
            ]:
                text_detail = re.sub(regex, replaced, text_detail)

        """Find multiple mailto or http links like <mailto:xyz@convo.com|xyz@convo.com> or '<http://url.com|url.com>in text and substitute it with original content
        """

        path = r"(\<(?:mailto|http|https):\/\/.*?\|.*?\>)"
        combination = re.findall(path, text_detail)

        if combination:
            for remove in combination:
                replaced = remove.split("|")[1]
                replaced = replaced.replace(">", "")
                text_detail = text_detail.replace(remove, replaced)
        return text_detail.strip()

    @staticmethod
    def is_interact_msg(payload: Dict) -> bool:
        """Check wheter the input is a support interactive input type."""

        support = [
            "button",
            "select",
            "static_select",
            "external_select",
            "conversations_select",
            "users_select",
            "channels_select",
            "overflow",
            "datepicker",
        ]
        if payload.get("actions"):
            action_type = payload["actions"][0].get("type")
            if action_type in support:
                return True
            elif action_type:
                log.warning(
                    "Received input from a Slack interactive component of type "
                    f"'{payload['actions'][0]['type']}', for which payload parsing is not yet support."
                )
        return False

    @staticmethod
    def _get_interact_resp(action: Dict) -> Optional[Text]:
        """Parse the payload for the response value."""

        if action["type"] == "button":
            return action.get("value")
        elif action["type"] == "select":
            return action.get("selected_options", [{}])[0].get("value")
        elif action["type"] == "static_select":
            return action.get("selected_option", {}).get("value")
        elif action["type"] == "external_select":
            return action.get("selected_option", {}).get("value")
        elif action["type"] == "conversations_select":
            return action.get("selected_conversation")
        elif action["type"] == "users_select":
            return action.get("selected_user")
        elif action["type"] == "channels_select":
            return action.get("selected_channel")
        elif action["type"] == "overflow":
            return action.get("selected_option", {}).get("value")
        elif action["type"] == "datepicker":
            return action.get("selected_date")

    async def task_msg(
        self,
        request: Request,
        on_new_message: Callable[[UserMsg], Awaitable[Any]],
        text,
        sender_id: Optional[Text],
        metadata: Optional[Dict],
    ) -> Any:
        """Slack retries to post messages up to 3 times based on
        failure conditions defined here:
        https://api.slack.com/events-api#failure_conditions
        """
        retry_detail = request.headers.get(self.retry_reason_header)
        total_retry = request.headers.get(self.retry_num_header)
        if total_retry and retry_detail in self.errors_ignore_retry:
            log.warning(
                f"Received retry #{total_retry} request from slack"
                f" due to {retry_detail}."
            )

            return response.text(None, status=201, headers={"X-Slack-No-Retry": 1})

        if metadata is not None:
            output_socket = metadata.get("out_channel")
            if self.use_threads:
                thread_id = metadata.get("thread_id")
            else:
                thread_id = None
        else:
            output_socket = None
            thread_id = None

        try:
            user_msg = UserMsg(
                text,
                self.fetch_output_channel(output_socket, thread_id),
                sender_id,
                input_channel=self.name(),
                metadata=metadata,
            )

            await on_new_message(user_msg)
        except Exception as e:
            log.error(f"Exception when trying to handle message.{e}")
            log.error(str(e), exc_info=True)

        return response.text("")

    def get_metadata(self, request: Request) -> Dict[Text, Any]:
        """Extracts the metadata from a slack API event (https://api.slack.com/types/event).

        Args:
            request: A `Request` object that contains a slack API event in the body.

        Returns:
            Metadataset extracted from the sent event pay_load. This includes the out_put channel for the response,
            and users that have installed the bot.
        """
        contentType = request.headers.get("content-type")

        # Slack API sends either a JSON-encoded or a URL-encoded body depending on the content
        if contentType == "application/json":
            # if JSON-encoded message is received
            slack_task = request.json
            event = slack_task.get("event", {})
            thread_id = event.get("thread_ts", event.get("ts"))

            users = []
            if "authed_users" in slack_task:
                users = slack_task.get("authed_users")
            elif (
                "authorizations" in slack_task
                and len(slack_task.get("authorizations")) > 0
            ):
                users.append(slack_task.get("authorizations")[0].get("user_id"))

            return {
                "out_channel": event.get("channel"),
                "thread_id": thread_id,
                "users": users,
            }
        
        if contentType == "application/x-www-form-urlencoded":
            # if URL-encoded message is received
            out_put = request.form
            pay_load = json.loads(out_put["payload"][0])
            message = pay_load.get("message", {})
            thread_id = message.get("thread_ts", message.get("ts"))

            users = []
            if pay_load.get("user", {}).get("id"):
                users.append(pay_load.get("user", {}).get("id"))

            return {
                "out_channel": pay_load.get("channel", {}).get("id"),
                "thread_id": thread_id,
                "users": users,
            }

        return {}

    def blue_print(
        self, on_new_message: Callable[[UserMsg], Awaitable[Any]]
    ) -> Blueprint:
        slack_task_web_hook = Blueprint("slack_webhook", __name__)

        @slack_task_web_hook.route("/", methods=["GET"])
        async def get_health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @slack_task_web_hook.route("/webhook", methods=["GET", "POST"])
        async def web_hook_service(request: Request) -> HTTPResponse:
            contentType = request.headers.get("content-type")
            # Slack API sends either a JSON-encoded or a URL-encoded body depending on the content

            if contentType == "application/json":
                # if JSON-encoded message is received
                out_put = request.json
                event = out_put.get("event", {})
                user_msg = event.get("text", "")
                sender_id = event.get("user", "")
                metadata = self.get_metadata(request)

                if "challenge" in out_put:
                    return response.json(out_put.get("challenge"))

                if not self._is_user_msg(out_put):
                    log.debug(
                        "Received message from Slack which doesn't look like "
                        "a user message. Skipping message."
                    )
                    return response.text("Bot message delivered.")

                if not self.is_support_socket(out_put, metadata):
                    log.warning(
                        f"Received message on unsupported "
                        f"channel: {metadata['out_channel']}"
                    )
                    return response.text("channel not supported.")

                return await self.task_msg(
                    request,
                    on_new_message,
                    text=self._clean_user_msg(user_msg, metadata["users"]),
                    sender_id=sender_id,
                    metadata=metadata,
                )

            elif contentType == "application/x-www-form-urlencoded":
                # if URL-encoded message is received
                out_put = request.form
                pay_load = json.loads(out_put["payload"][0])

                if self.is_interact_msg(pay_load):
                    sender_id = pay_load["user"]["id"]
                    detail_text = self._get_interact_resp(pay_load["actions"][0])
                    if detail_text is not None:
                        metadata = self.get_metadata(request)
                        return await self.task_msg(
                            request, on_new_message, detail_text, sender_id, metadata
                        )
                    if pay_load["actions"][0]["type"] == "button":
                        # link buttons don't have "value", don't send their clicks to bot
                        return response.text("User clicked link button")
                return response.text(
                    "The input message could not be processed.", status=500
                )

            return response.text("Bot message delivered.")

        return slack_task_web_hook

    def is_support_socket(self, slack_event: Dict, metadata: Dict) -> bool:
        return (
            self._is_direct_msg(slack_event)
            or self._is_application_mentioned(slack_event)
            or metadata["out_channel"] == self.slack_channel
        )

    def fetch_output_channel(
        self, socket: Optional[Text] = None, thread_id: Optional[Text] = None
    ) -> OutputSocket:
        socket = socket or self.slack_channel
        return BotSlack(self.slack_token, socket, thread_id, self.proxy)

    def set_output_socket(self, channel: Text) -> None:
        self.slack_channel = channel
