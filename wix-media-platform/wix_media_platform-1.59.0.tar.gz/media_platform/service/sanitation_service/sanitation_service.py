from __future__ import annotations

from media_platform.auth.app_authenticator import AppAuthenticator
from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.sanitation_service.sanitation_request import SanitationRequest
from media_platform.service.media_platform_service import MediaPlatformService


class SanitationService(MediaPlatformService):
    def __init__(self, domain: str, authenticated_http_client: AuthenticatedHTTPClient):
        super().__init__(domain, authenticated_http_client)

    def sanitation_request(self) -> SanitationRequest:
        return SanitationRequest(self._authenticated_http_client, self._base_url)
