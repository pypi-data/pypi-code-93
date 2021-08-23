from __future__ import annotations

from typing import Dict, List

from media_platform.lang.serialization import Deserializable
from media_platform.service.file_descriptor import FileDescriptor


class CreateFilesResponse(Deserializable):
    def __init__(self, file_descriptors: List[FileDescriptor]):
        self.file_descriptors = file_descriptors

    @classmethod
    def deserialize(cls, data: Dict) -> CreateFilesResponse:
        return cls([FileDescriptor.deserialize(f) for f in data['files']])
