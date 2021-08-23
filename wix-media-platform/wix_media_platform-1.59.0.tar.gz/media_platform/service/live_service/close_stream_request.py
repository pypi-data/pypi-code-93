from __future__ import annotations

from typing import cast

from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.media_platform_request import MediaPlatformRequest


class CloseStreamRequest(MediaPlatformRequest):
    def __init__(self, authenticated_http_client: AuthenticatedHTTPClient, base_url: str, stream_id: str = None,
                 version: str = None, abort: bool = False):
        super().__init__(authenticated_http_client, 'DELETE', base_url + '/live/streams/', None)

        self.stream_id = stream_id
        self.version = version
        self.abort = abort

        self._url = base_url + '/live/streams/'

    def set_stream_id(self, stream_id: str) -> CloseStreamRequest:
        self.stream_id = stream_id
        return self

    def set_version(self, version: str) -> CloseStreamRequest:
        self.version = version
        return self

    def set_abort(self, abort: bool) -> CloseStreamRequest:
        self.abort = abort
        return self

    def execute(self) -> CloseStreamRequest:
        self.url = self._url + self.stream_id
        query_string = self._query_string()

        if query_string:
            self.url += '?' + query_string

        return cast(CloseStreamRequest, super().execute())

    def _query_string(self) -> str:
        query_string = ''
        if self.version:
            query_string += 'version=' + self.version

        if self.abort:
            query_string += 'abort=True'

        return query_string
