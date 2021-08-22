"""Slack client."""
import logging
import traceback

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse


class SlackNotification:
    """Slack notification."""

    def __init__(self, bot_token: str, channel: str) -> None:
        self.client = SlackClient(bot_token, channel)

    def post_error(self, exception: Exception):
        type_exception = exception.__class__.__name__
        error_message = str(exception)
        response = self.client.post_message(f"{type_exception}: {error_message}")
        joined_traceback = "\n".join(traceback.format_tb(exception.__traceback__))
        response = self.client.post_reply(f"```{joined_traceback}```", response["message"]["ts"])


class SlackClient:
    """Slack client."""

    def __init__(self, bot_token: str, channel: str) -> None:
        self.client = WebClient(token=bot_token)
        self.channel = channel
        self.logger = logging.getLogger(__name__)

    def post_message(self, message) -> SlackResponse:
        try:
            return self.client.chat_postMessage(channel=self.channel, text=message)
        except SlackApiError as error:
            raise self.process_slack_api_error(error)

    def post_reply(self, message: str, thread_timestamp: str) -> SlackResponse:
        try:
            return self.client.chat_postMessage(channel=self.channel, text=message, thread_ts=thread_timestamp)
        except SlackApiError as error:
            raise self.process_slack_api_error(error)

    def process_slack_api_error(self, error: SlackApiError) -> SlackApiError:
        # You will get a SlackApiError if "ok" is False
        assert error.response["ok"] is False
        assert error.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        self.logger.error(error.response["error"])
        self.logger.exception(error)
        return error
