from __future__ import annotations

from typing import Dict, Optional

from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.file_descriptor import FileDescriptor
from media_platform.service.lifecycle import Lifecycle
from media_platform.service.media_platform_request import MediaPlatformRequest


class AddLifecycleRequest(MediaPlatformRequest):
    def __init__(self, authenticated_http_client: AuthenticatedHTTPClient, base_url: str, lifecycle: Lifecycle,
                 file_id: Optional[str] = None, path: Optional[str] = None):
        super().__init__(authenticated_http_client, 'POST', base_url + '/files/lifecycle', FileDescriptor)

        self.file_id = file_id
        self.path = path
        self.lifecycle = lifecycle

    def _params(self) -> Dict:
        return {
            'id': self.file_id,
            'path': self.path,
            'lifecycle': self.lifecycle.serialize() if self.lifecycle else None
        }
