from __future__ import annotations
from typing import List, Dict

from media_platform.lang.serialization import Deserializable
from media_platform.service.file_descriptor import FileDescriptor


class FileList(Deserializable):
    def __init__(self, files: [FileDescriptor]):
        self.files = files

    @classmethod
    def deserialize(cls, data: List[Dict]) -> FileList:
        return FileList([FileDescriptor.deserialize(f) for f in data])
