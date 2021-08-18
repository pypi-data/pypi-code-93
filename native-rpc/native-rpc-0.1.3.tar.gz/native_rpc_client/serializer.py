import json
import pickle
from io import TextIOWrapper
from typing import Any, BinaryIO


class Serializer:
    def __init__(self):
        pass

    @property
    def content_type(self) -> str:
        return 'application/octet-stream'

    def serialize(self, obj: Any, writer: BinaryIO) -> None:
        pass


class JsonSerializer(Serializer):
    def __init__(self, encoding='utf-8'):
        super().__init__()
        self._encoding = encoding

    @property
    def content_type(self) -> str:
        return 'application/json'

    def serialize(self, obj: Any, writer: BinaryIO) -> None:
        wrapper = TextIOWrapper(writer, write_through=True, encoding=self._encoding)
        json.dump(obj, wrapper)
        wrapper.detach()


class PickleSerializer(Serializer):
    def __init__(self):
        super().__init__()

    @property
    def content_type(self) -> str:
        return 'application/x-pickle'

    def serialize(self, obj: Any, writer: BinaryIO) -> None:
        return pickle.dump(obj, writer)
