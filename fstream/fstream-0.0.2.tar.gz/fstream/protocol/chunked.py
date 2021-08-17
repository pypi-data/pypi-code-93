from asyncio import Protocol
from fstream.protocol.base import BaseStreamProtocol


class ChunkedStreamProtocol(BaseStreamProtocol, Protocol):
    __slots__ = ()

    def __init__(self, loop, connected_cb) -> None:
        super().__init__(loop, connected_cb)

    def data_received(self, data: bytes) -> None:
        self.data_buffer += data

        if self._data_future is not None:
            self._data_future.set_result(None)
            self._data_future = None
        else:
            self._transport.pause_reading()
