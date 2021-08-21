from asyncio import Transport
from asyncio.exceptions import LimitOverrunError
from types import coroutine
from typing import Any, Awaitable, List, Optional, Union


# Awaitable with instant return
_completed = coroutine(lambda: None if True else (yield))()


class BaseStreamProtocol:
    __slots__ = (
        '_loop',
        '_client_connected_cb',

        '_transport',
        '_closed',
        '_exc',
        '_writing_paused',

        '_data_future',
        '_drain_future',
        '_close_future',

        'data_buffer'
    )

    def __init__(self, loop, connected_cb) -> None:
        self._loop = loop
        self._client_connected_cb = connected_cb

        self._transport = None
        self._closed = False
        self._exc = None
        self._writing_paused = False

        self._data_future = None
        self._drain_future = None
        self._close_future = None

        self.data_buffer = bytearray()

    @property
    def transport(self) -> Transport:
        return self.transport

    def connection_made(self, transport) -> None:
        self._transport = transport

        if self._client_connected_cb is not None:
            self._loop.create_task(self._client_connected_cb(
                StreamReader(self),
                StreamWriter(self),
            ))

    def connection_lost(self, exc) -> None:
        self._exc = exc
        self._closed = True

        if exc is not None:
            if self._data_future is not None:
                self._data_future.set_exception(exc)
            if self._drain_future is not None:
                self._drain_future.set_exception(exc)
            if self._close_future is not None:
                self._close_future.set_exception(exc)
        else:
            if self._data_future is not None:
                self._data_future.set_result(None)
            if self._drain_future is not None:
                self._drain_future.set_result(None)
            if self._close_future is not None:
                self._close_future.set_result(None)

    def pause_writing(self) -> None:
        self._writing_paused = True

    def resume_writing(self) -> None:
        self._writing_paused = False

        if self._drain_future is not None:
            self._drain_future.set_result(None)
            self._drain_future = None

    def wait_data_notify(self) -> Awaitable:
        if self._closed:
            raise self._exc or ConnectionResetError('Connection lost')

        if self._data_future is None:
            self._data_future = self._loop.create_future()
            self._transport.resume_reading()

        return self._data_future

    def wait_drain_notify(self) -> Awaitable:
        if self._closed:
            raise self._exc or ConnectionResetError('Connection lost')

        if not self._writing_paused:
            return _completed

        if self._drain_future is None:
            self._drain_future = self._loop.create_future()

        return self._drain_future

    def wait_close_notify(self) -> Awaitable:
        if self._closed:
            if self._exc is not None:
                raise self._exc
            else:
                return _completed

        if self._close_future is None:
            self._close_future = self._loop.create_future()

        return self._close_future

    def get_exception(self) -> Optional[Exception]:
        return self._exc


class StreamReader:
    __slots__ = ('protocol',)

    def __init__(self, protocol: BaseStreamProtocol) -> None:
        self.protocol = protocol

    async def readuntil(self, separator=b'\n', include_delimiter=True, limit=1024*1024) -> bytearray:
        data_buffer = self.protocol.data_buffer
        sep_len = len(separator)
        sep_index = data_buffer.find(separator)

        while sep_index == -1:
            data_len = len(data_buffer)
            if data_len > limit:
                raise LimitOverrunError(
                    'Separator is not found, and chunk exceed the limit', data_len)

            await self.protocol.wait_data_notify()
            sep_start = 0 if sep_len > data_len else data_len - sep_len
            sep_index = data_buffer.find(separator, sep_start)

        buffer_len = sep_index + sep_len
        buffer = data_buffer[:buffer_len if include_delimiter else sep_index]
        del data_buffer[:buffer_len]

        return buffer

    async def read(self, nbytes: int) -> bytearray:
        if nbytes < 1:
            raise ValueError('read size has to be greater than zero')

        data_buffer = self.protocol.data_buffer
        buffer_len = len(data_buffer)

        if buffer_len == 0:
            await self.protocol.wait_data_notify()
            buffer_len = len(data_buffer)

        read_len = nbytes if nbytes < buffer_len else buffer_len
        buffer = data_buffer[:read_len]
        del data_buffer[:read_len]

        return buffer

    async def readexactly(self, nbytes: int) -> bytearray:
        if nbytes < 1:
            raise ValueError('readexactly size has to be greater than zero')

        data_buffer = self.protocol.data_buffer

        while len(data_buffer) < nbytes:
            await self.protocol.wait_data_notify()

        buffer = data_buffer[:nbytes]
        del data_buffer[:nbytes]

        return buffer

    async def readlen(self, limit: int = 1024*1024, endian='little') -> Union[bytearray, bytes]:
        """
        Reads length prefixed message from the stream.
        [u32: length | payload bytes ]
        """

        if limit < 1:
            raise ValueError('limit size has to be greater than zero')

        data_buffer = self.protocol.data_buffer
        while len(data_buffer) < 4:
            await self.protocol.wait_data_notify()

        buffer_len = int.from_bytes(data_buffer[:4], endian)
        if buffer_len > limit:
            raise LimitOverrunError('buffer length exceed the limit', buffer_len)
        elif buffer_len == 0:
            del data_buffer[:4]
            return b''

        read_len = buffer_len + 4
        while len(data_buffer) < read_len:
            await self.protocol.wait_data_notify()

        buffer = data_buffer[4:read_len]
        del data_buffer[:read_len]

        return buffer


class StreamWriter:
    __slots__ = ('protocol',)

    def __init__(self, protocol: BaseStreamProtocol) -> None:
        self.protocol = protocol

    def close(self) -> None:
        self.protocol._transport.close()

    def is_closing(self) -> bool:
        return self.protocol._transport.is_closing()

    def can_write_eof(self) -> bool:
        return self.protocol._transport.can_write_eof()

    def get_extra_info(self, name, default=None) -> Any:
        return self.protocol._transport.get_extra_info(name, default)

    def write(self, buffer: Union[bytes, bytearray]) -> None:
        self.protocol._transport.write(buffer)

    def writelines(self, buffers: List[Any]) -> None:
        self.protocol._transport.writelines(buffers)

    def writelen(self, buffer: Union[bytes, bytearray], endian='little') -> None:
        """
        Writes length prefixed message to stream.
        [u32: length | payload bytes ]
        """
        self.protocol._transport.write(len(buffer).to_bytes(4, endian))
        self.protocol._transport.write(buffer)

    def write_eof(self) -> None:
        return self.protocol._transport.write_eof()

    def drain(self) -> Awaitable:
        return self.protocol.wait_drain_notify()

    def wait_closed(self) -> Awaitable:
        return self.protocol.wait_close_notify()
