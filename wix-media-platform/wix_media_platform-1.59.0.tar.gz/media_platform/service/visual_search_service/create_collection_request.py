from __future__ import annotations

from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.visual_search_service.collection import Collection
from media_platform.service.media_platform_request import MediaPlatformRequest


class CreateCollectionRequest(MediaPlatformRequest):
    def __init__(self, authenticated_http_client: AuthenticatedHTTPClient, base_url: str):
        super().__init__(authenticated_http_client, 'POST', f'{base_url}/visual_search', Collection)

        self.collection_id = None
        self.name = None
        self.project_id = None
        self.model_id = None

    def set_collection_id(self, collection_id: str) -> CreateCollectionRequest:
        self.collection_id = collection_id
        return self

    def set_name(self, name: str) -> CreateCollectionRequest:
        self.name = name
        return self

    def set_project_id(self, project_id: str) -> CreateCollectionRequest:
        self.project_id = project_id
        return self

    def set_model_id(self, model_id: str) -> CreateCollectionRequest:
        self.model_id = model_id
        return self

    def execute(self):
        self.url = f'{self.url}/collections'
        return super().execute()

    def _params(self) -> dict:
        return {
            'id': self.collection_id,
            'name': self.name,
            'projectId': self.project_id,
            'modelId': self.model_id,
        }
