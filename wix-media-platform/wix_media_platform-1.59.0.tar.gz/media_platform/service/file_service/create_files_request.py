from __future__ import annotations

from typing import List, Iterable

from media_platform.exception.conflict_exception import ConflictException
from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.file_descriptor import FileDescriptor
from media_platform.service.file_service.create_file_request import CreateFileRequest
from media_platform.service.file_service.create_files_response import CreateFilesResponse
from media_platform.service.media_platform_request import MediaPlatformRequest


class CreateFilesRequest(MediaPlatformRequest):
    def __init__(self, authenticated_http_client: AuthenticatedHTTPClient, base_url: str):
        super().__init__(authenticated_http_client, 'POST', base_url + '/files', FileDescriptor)
        self.file_requests = []

    def execute(self) -> CreateFilesResponse:
        file_descriptors = list(self._post())
        return CreateFilesResponse(file_descriptors)

    def set_file_requests(self, file_requests: List[CreateFileRequest]) -> CreateFilesRequest:
        self.file_requests = file_requests
        return self

    def add_file(self, *file_request: [CreateFileRequest]) -> CreateFilesRequest:
        self.file_requests.extend(file_request)
        return self

    def _params(self):
        return {
            'files': [request._params() for request in self.file_requests]
        }

    def _post(self) -> Iterable[FileDescriptor]:
        # TODO: Replace with single request once server supports that
        for request in self.file_requests:
            try:
                yield self.authenticated_http_client.post(self.url, request._params(), self.response_payload_type)

            except ConflictException:
                pass
