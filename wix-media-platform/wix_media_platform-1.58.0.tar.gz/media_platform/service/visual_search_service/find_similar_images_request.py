from __future__ import annotations

from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.visual_search_service.file_list import FileList
from media_platform.service.media_platform_request import MediaPlatformRequest


class FindSimilarImagesRequest(MediaPlatformRequest):
    def __init__(self, authenticated_http_client: AuthenticatedHTTPClient, base_url: str):
        super().__init__(authenticated_http_client, 'POST', f'{base_url}/visual_search', FileList)

        self.image_url = None
        self.collection_id = None

    def set_image_url(self, image_url: str) -> FindSimilarImagesRequest:
        self.image_url = image_url
        return self

    def set_collection_id(self, collection_id: str) -> FindSimilarImagesRequest:
        self.collection_id = collection_id
        return self

    def execute(self):
        self.url = f'{self.url}/collections/{self.collection_id}/search'
        return super().execute()

    def _params(self) -> dict:
        return {
            'imageUrl': self.image_url,
        }
