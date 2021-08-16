from __future__ import annotations

from typing import cast

from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.live_service.live_stream_analytics import LiveStreamAnalytics
from media_platform.service.media_platform_request import MediaPlatformRequest


class GetStreamAnalyticsRequest(MediaPlatformRequest):
    def __init__(self, authenticated_http_client: AuthenticatedHTTPClient, base_url: str, stream_id: str,
                 version: str = None):
        super().__init__(authenticated_http_client, 'GET', base_url + '/live/streams/', LiveStreamAnalytics)
        self.id = stream_id
        self.version = version
        self._url = self.url

    def execute(self) -> LiveStreamAnalytics:
        self.url = self._url + self.id + '/analytics'
        if self.version:
            self.url += '?version=' + self.version

        return cast(LiveStreamAnalytics, super().execute())
