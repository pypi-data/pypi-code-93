from __future__ import annotations

from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.media_platform_request import MediaPlatformRequest
from media_platform.service.visual_search_service.model import Model


class CreateModelRequest(MediaPlatformRequest):
    def __init__(self, authenticated_http_client: AuthenticatedHTTPClient, base_url: str):
        super().__init__(authenticated_http_client, 'POST', f'{base_url}/visual_search', Model)

        self.model_id = None
        self.name = None
        self.description = None

    def set_model_id(self, model_id: str) -> CreateModelRequest:
        self.model_id = model_id
        return self

    def set_name(self, name: str) -> CreateModelRequest:
        self.name = name
        return self

    def set_description(self, description: str) -> CreateModelRequest:
        self.description = description
        return self

    def execute(self):
        self.url = f'{self.url}/models'
        return super().execute()

    def _params(self) -> dict:
        return {
            'id': self.model_id,
            'name': self.name,
            'description': self.description,
        }
