import asyncio
from typing import Callable, Optional, Union

from aioconsole import get_standard_streams

from jsonrpcstdio.message import Notification, Request, Response, ResponseError
from jsonrpcstdio.errors import JSONRPCError, MethodNotFoundError, InvalidParamsError


class StdioJSONRPCServer:
    def __init__(self):
        self.jsonrpcserver = JSONRPCServer()

    def __getattr__(self, item):
        return getattr(self.jsonrpcserver, item)

    async def run(self):
        reader, writer = await get_standard_streams()
        await self.jsonrpcserver.run(reader, writer)


class JSONRPCServer:
    def __init__(self, reader=None, writer=None):
        self.methods = {}
        self.reader = reader
        self.writer = writer

    def register(self, method: str):
        def deco(func: Callable):
            self.methods[method] = func
            return func
        return deco

    async def process_incoming(self, incoming: Union[Request, Notification]):
        func = self.methods.get(incoming.method)
        if func is None:
            error = MethodNotFoundError(f'Method {incoming.method} not found')
            error.associated_request = incoming
            raise error
        try:
            if isinstance(incoming.params, list):
                result = await func(*incoming.params)
            elif isinstance(incoming.params, dict):
                result = await func(**incoming.params)
            else:
                raise InvalidParamsError
        except (TypeError, InvalidParamsError):
            error = InvalidParamsError
            error.associated_request = incoming
            raise error
        if result and isinstance(incoming, Request):
            return Response(id=incoming.id, result=result)

    def process_error(self, error: JSONRPCError) -> Optional[Response]:
        if error.associated_request is not None:
            if isinstance(error.associated_request, Notification):
                return None
            else:
                response_error = ResponseError(code=error.code, message=error.message)
                return Response(id=error.associated_request.id, error=response_error)
        else:
            response_error = ResponseError(code=error.code, message=error.message)
            return Response(id=None, error=response_error)

    async def run(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        def is_request(inc): return b'id' in inc

        self.reader, self.writer = reader, writer
        while True:
            incoming = await self.reader.read()
            if incoming:
                try:
                    if is_request(incoming):
                        request = Request.decode(incoming)
                        response = await self.process_incoming(request)
                    else:  # otherwise a Notification
                        notification = Notification.decode(incoming)
                        await self.process_incoming(notification)
                        response = None
                    if response is not None:
                        self.writer.write(response.encode())
                        await self.writer.drain()
                except JSONRPCError as err:
                    response = self.process_error(err)
                    if response is not None:
                        self.writer.write(response.encode())
                        await self.writer.drain()
