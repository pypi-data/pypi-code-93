import json
import pickle
from typing import Any

from aiohttp.streams import StreamReader


class Deserializer:
    def __init__(self):
        pass

    def __repr__(self):
        return f'<{type(self).__name__} {self.content_type}>'

    @property
    def content_type(self) -> str:
        return 'application/octet-stream'

    async def deserialize(self, data: StreamReader) -> Any:
        pass


class JsonDeserializer(Deserializer):
    def __init__(self):
        super().__init__()

    @property
    def content_type(self) -> str:
        return 'application/json'

    async def deserialize(self, data: StreamReader) -> Any:
        return json.loads(await data.read())


class PickleDeserializer(Deserializer):
    def __init__(self):
        super().__init__()

    @property
    def content_type(self) -> str:
        return 'application/x-pickle'

    async def deserialize(self, data: StreamReader) -> Any:
        return pickle.loads(await data.read())
