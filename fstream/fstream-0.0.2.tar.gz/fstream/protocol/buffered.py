from threading import local
from asyncio import BufferedProtocol
from fstream.protocol.base import BaseStreamProtocol


# Thread-local storage for shared buffers.
_tlocal = local()


def _get_buffer() -> memoryview:
    try:
        buffer = _tlocal.buffer
    except AttributeError:
        buffer = memoryview(bytearray(1024*256))
        _tlocal.buffer = buffer

    return buffer


class BufferedStreamProtocol(BaseStreamProtocol, BufferedProtocol):
    __slots__ = (
        '_recv_buffer',
    )

    def __init__(self, loop=None, connected_cb=None, get_buffer=_get_buffer) -> None:
        super().__init__(loop, connected_cb)

        self._recv_buffer = get_buffer()

    def get_buffer(self, _) -> bytearray:
        return self._recv_buffer

    def buffer_updated(self, nbytes: int) -> None:
        self.data_buffer += self._recv_buffer[:nbytes]

        if self._data_future is not None:
            self._data_future.set_result(None)
            self._data_future = None
        else:
            self._transport.pause_reading()
