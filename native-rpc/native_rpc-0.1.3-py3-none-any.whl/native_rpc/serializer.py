import json
import pickle
from typing import Any

from native_rpc.stream import StreamWriter


class Serializer:
    def __init__(self):
        pass

    def __repr__(self):
        return f'<{type(self).__name__} {self.content_type}>'

    @property
    def content_type(self) -> str:
        return 'application/octet-stream'

    async def serialize(self, obj: Any, writer: StreamWriter) -> None:
        await writer.write(await self.serialize_bytes(obj))

    async def serialize_bytes(self, obj: Any) -> bytes:
        pass


class JsonSerializer(Serializer):
    def __init__(self):
        super().__init__()

    @property
    def content_type(self) -> str:
        return 'application/json'

    async def serialize_bytes(self, obj: Any) -> bytes:
        return json.dumps(obj).encode('utf-8')


class PickleSerializer(Serializer):
    def __init__(self):
        super().__init__()

    @property
    def content_type(self) -> str:
        return 'application/x-pickle'

    async def serialize_bytes(self, obj: Any) -> bytes:
        return pickle.dumps(obj)
