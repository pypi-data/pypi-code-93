import os
import asyncio
from typing import Callable, Coroutine, Tuple, Union
from fstream.protocol import StreamReader, StreamWriter, ChunkedStreamProtocol, BufferedStreamProtocol, _get_buffer


# Info
__version__ = '0.0.3'
__author__ = '33TU'


# typing
GetBuffer = Callable[[], Union[memoryview, bytearray]]
ConnectedCb = Callable[[StreamReader, StreamWriter], Coroutine]


async def open_connection_buffered(*args, get_buffer: GetBuffer = _get_buffer, loop=None, **kwargs) -> Tuple[StreamReader, StreamWriter]:
    """
    Open stream using BufferedStreamProtocol.
    """
    loop = loop or asyncio.get_running_loop()
    proto = BufferedStreamProtocol(loop, None, get_buffer)

    await loop.create_connection(lambda: proto, *args, **kwargs)

    return (StreamReader(proto), StreamWriter(proto),)


async def start_server_buffered(client_connected_cb: ConnectedCb,
                       *args, get_buffer: GetBuffer = _get_buffer, loop=None, **kwargs) -> asyncio.AbstractServer:
    """
    Start server which uses BufferedStreamProtocol.
    """
    loop = loop or asyncio.get_running_loop()

    return await loop.create_server(
        lambda: BufferedStreamProtocol(loop, client_connected_cb, get_buffer),
        *args,
        **kwargs
    )
    

async def open_connection_chunked(*args, loop=None, **kwargs) -> Tuple[StreamReader, StreamWriter]:
    """
    Open stream using ChunkedProtocol.
    """
    loop = loop or asyncio.get_running_loop()
    proto = ChunkedStreamProtocol(loop, None)

    await loop.create_connection(lambda: proto, *args, **kwargs)

    return (StreamReader(proto), StreamWriter(proto),)


async def start_server_chunked(client_connected_cb: ConnectedCb,
                       *args, loop=None, **kwargs) -> asyncio.AbstractServer:
    """
    Start server which uses ChunkedStreamProtocol.
    """
    loop = loop or asyncio.get_running_loop()

    return await loop.create_server(
        lambda: ChunkedStreamProtocol(loop, client_connected_cb),
        *args,
        **kwargs
    )


# OS SPECIFIC DEFAULTS
prefer_chunked = os.name == 'nt' # Prefer asyncio.Protocol over asyncio.BufferedProtocol on windows.
open_connection = open_connection_chunked if prefer_chunked else open_connection_buffered
start_server = start_server_chunked if prefer_chunked else start_server_buffered