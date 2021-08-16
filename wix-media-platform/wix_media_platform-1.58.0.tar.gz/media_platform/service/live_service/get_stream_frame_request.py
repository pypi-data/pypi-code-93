from __future__ import annotations

from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.media_platform_request import MediaPlatformRequest


class GetStreamFrameRequest(MediaPlatformRequest):
    def __init__(self, authenticated_http_client: AuthenticatedHTTPClient, base_url: str, stream_id: str,
                 version: str = None):
        super().__init__(authenticated_http_client, 'GET', base_url + '/live/streams/', bytes)
        self.id = stream_id
        self.version = version
        self._url = self.url

    def execute(self) -> bytes:
        self.url = self._url + self.id + '/frame'
        if self.version:
            self.url += '?version=' + self.version

        return super().execute()
