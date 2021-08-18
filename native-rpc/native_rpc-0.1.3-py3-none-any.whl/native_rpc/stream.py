from aiohttp import web


class StreamWriter:
    def __init__(self) -> None:
        pass

    async def write(self, data: bytes) -> None:
        pass


class ResponseStreamWriter(StreamWriter):
    def __init__(self, response: web.StreamResponse) -> None:
        super().__init__()
        self._response = response

    async def write(self, data: bytes) -> None:
        await self._response.write(data)


class BytesStreamWriter(StreamWriter):
    def __init__(self, data: bytes = b'') -> None:
        super().__init__()
        self._data = data

    async def write(self, data: bytes) -> None:
        self._data += data

    @property
    def data(self):
        return self._data
