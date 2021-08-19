from typing import List

import pydash as __

from . import channel_manager
from .types import NotificationChannel, Notification

__all__ = ['SNSNotification', 'Notification', 'NotificationChannel']


class SNSNotification:
    def __init__(self, **kwargs):
        self._cache_send_channels = {}
        self._configs = __.clone_deep(kwargs)

    def send(self, notification: Notification):
        if callable(notification.via):
            channels = notification.via()
        else:
            channels = notification.via
        for channel in self._get_channels(channels):
            channel.send(notification)

    def reset_cache(self):
        self._cache_send_channels = {}

    def _get_channels(self, via_channels: List[str]) -> List[NotificationChannel]:
        results = []
        for key in via_channels:
            if key in self._cache_send_channels:
                channel = self._cache_send_channels[key]
                if channel is not None:
                    results.append(channel)
            else:
                channel = channel_manager.create_channel(key, self._configs)
                self._cache_send_channels[key] = channel
                if channel is not None:
                    results.append(channel)

        return results
