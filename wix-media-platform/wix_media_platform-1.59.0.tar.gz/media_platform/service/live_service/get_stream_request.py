from __future__ import annotations

from typing import cast

from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.live_service.live_stream import LiveStream
from media_platform.service.media_platform_request import MediaPlatformRequest


class GetStreamRequest(MediaPlatformRequest):
    def __init__(self, authenticated_http_client: AuthenticatedHTTPClient, base_url: str):
        super().__init__(authenticated_http_client, 'GET', base_url + '/live/streams/', LiveStream)
        self.id = None
        self.version = None
        self._url = self.url

    def set_id(self, stream_id: str) -> GetStreamRequest:
        self.id = stream_id
        return self

    def set_version(self, version: str) -> GetStreamRequest:
        self.version = version
        return self

    def execute(self) -> LiveStream:
        self.url = self._url + self.id
        if self.version:
            self.url += '?version=' + self.version

        return cast(LiveStream, super().execute())

