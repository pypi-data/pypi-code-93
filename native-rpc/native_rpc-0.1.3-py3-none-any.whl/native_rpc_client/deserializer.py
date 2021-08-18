import json
import pickle
from typing import Any, BinaryIO


class Deserializer:
    def __init__(self):
        pass

    @property
    def content_type(self) -> str:
        return 'application/octet-stream'

    def deserialize(self, reader: BinaryIO) -> Any:
        pass


class JsonDeserializer(Deserializer):
    def __init__(self):
        super().__init__()

    @property
    def content_type(self) -> str:
        return 'application/json'

    def deserialize(self, reader: BinaryIO) -> Any:
        return json.load(reader)


class PickleDeserializer(Deserializer):
    def __init__(self):
        super().__init__()

    @property
    def content_type(self) -> str:
        return 'application/x-pickle'

    def deserialize(self, reader: BinaryIO) -> Any:
        return pickle.load(reader)
