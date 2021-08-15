from rfc3986 import urlparse
import asyncio
import socket

AVAILABLE_SCHEMES = ['tcp']
DEFAULT_TCP_PORT = 10000


class InvalidUri(Exception):
    pass


class UnavailableUriScheme(Exception):
    pass


class Reader:
    """
    Wraps asyncio.StreamReader
    """
    def __init__(self, reader):
        self.__reader = reader

    async def read(self) -> bytes:
        """
        Read frame from stream
        """
        header = await self.__reader.readexactly(4)
        length = int.from_bytes(header, byteorder='big', signed=False)
        return await self.__reader.readexactly(length)


class Writer:
    """
    Wraps asyncio.StreamWriter
    """
    def __init__(self, writer):
        self.__writer = writer

    def write(self, frame: bytes):
        """
        Write frame to stream
        """
        header = len(frame).to_bytes(4, byteorder='big')
        self.__writer.write(header)
        self.__writer.write(frame)

    async def drain(self):
        """
        Flush the write buffer.
        """
        await self.__writer.drain()

    async def close(self):
        """
        Close stream with confirmation
        """
        self.__writer.close()
        await self.__writer.wait_closed()

    def close_nowait(self):
        """
        Close stream without confirmation
        """
        self.__writer.close()

    def is_closing(self):
        """
        Check if stream closed
        """
        return self.__writer.is_closing()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.close_nowait()
        except:
            pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.close()
        except:
            pass


class ServerBase:
    async def run(self, loop=None):
        pass


class ServerTCP(ServerBase):
    """
    Wraps TCP server
    """
    def __init__(self, handle, host: str, port: int):
        self.__host = host
        self.__port = port
        self.__handle = handle

    async def _my_handle(self, reader, writer):
        await self.__handle(Reader(reader), Writer(writer))

    async def run(self, loop=None):
        """
        Run server
        """
        server = await asyncio.start_server(self._my_handle, self.__host, self.__port, loop=loop)
        async with server:
            await server.serve_forever()


async def connect_tcp(host: str, port: int, loop=None) -> (Reader, Writer):
    """
    Connect to SFP over TCP server
    Returns socket reader and writer objects
    """
    reader, writer = await asyncio.open_connection(host, port, loop=loop)
    return Reader(reader), Writer(writer)

if hasattr(socket, 'AF_UNIX'):
    AVAILABLE_SCHEMES.append('unix')

    class ServerUnix(ServerBase):
        """
        Wraps unix domain socket server
        """
        def __init__(self, handle, path: str):
            self.__path = path
            self.__handle = handle

        async def _my_handle(self, reader, writer):
            await self.__handle(Reader(reader), Writer(writer))

        async def run(self, loop=None):
            """
            Run server
            """
            server = await asyncio.start_unix_server(self._my_handle, self.__path, loop=loop)
            async with server:
                await server.serve_forever()


    async def connect_unix(path: str, loop=None) -> (Reader, Writer):
        """
        Connect to SFP over unix domain socket server
        Returns socket reader and writer objects
        """
        reader, writer = await asyncio.open_unix_connection(path, loop=loop)
        return Reader(reader), Writer(writer)


def get_server_from_uri(uri: str, handle) -> ServerBase:
    """
    Selecting server class based on uri
    """
    parsed = urlparse(uri)
    if parsed.scheme not in AVAILABLE_SCHEMES:
        raise UnavailableUriScheme(uri)
    if parsed.scheme == 'tcp':
        port = parsed.port
        if parsed.host is None:
            raise InvalidUri(uri)
        if parsed.port is None:
            port = DEFAULT_TCP_PORT
        return ServerTCP(handle, parsed.host, port)
    else:
        if parsed.host is None and parsed.path is None:
            raise InvalidUri(uri)
        if parsed.path is None:
            path = parsed.host
        elif parsed.host is None:
            path = parsed.path
        else:
            path = parsed.host + parsed.path
        return ServerUnix(handle, path)


def connect_to_uri(uri: str, loop=None) -> (Reader, Writer):
    """
    Selecting connection type based on uri
    """
    parsed = urlparse(uri)
    if parsed.scheme not in AVAILABLE_SCHEMES:
        raise UnavailableUriScheme(uri)
    if parsed.scheme == 'tcp':
        port = parsed.port
        if parsed.host is None:
            raise InvalidUri(uri)
        if parsed.port is None:
            port = DEFAULT_TCP_PORT
        return connect_tcp(parsed.host, port, loop=loop)
    else:
        if parsed.host is None and parsed.path is None:
            raise InvalidUri(uri)
        if parsed.path is None:
            path = parsed.host
        elif parsed.host is None:
            path = parsed.path
        else:
            path = parsed.host + parsed.path
        return connect_unix(path, loop=loop)
