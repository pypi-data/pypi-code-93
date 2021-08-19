from slack_sdk import WebClient

from SNSNotifications.types import NotificationChannel, Notification
from .message import SlackMessage

__all__ = ['SlackClient', 'SlackMessage']


class SlackClient(NotificationChannel):

    def __init__(self, token, channel="#random", **kwargs):
        self.default_channel = channel
        self.client = WebClient(token)

    def send(self, notification: Notification):
        if not self.can_send(notification):
            return
        msg: SlackMessage = getattr(notification, "to_{}".format(self.channel_identify()))()
        channel = msg.channel or self.default_channel
        payload = {}

        if msg.has_blocks:
            payload['blocks'] = msg.blocks
            if msg.has_mentions:
                payload['blocks'] = msg.with_mentions(msg.blocks)
        payload['text'] = msg.text
        if msg.has_mentions:
            payload['text'] = msg.with_mentions(msg.text)

        if msg.has_link:
            payload['link_names'] = 1

        self.client.chat_postMessage(channel=channel, **payload)

    def channel_identify(self) -> str:
        return "slack"
