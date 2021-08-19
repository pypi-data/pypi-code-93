""" Module implementing low-level connection to the server. """

from __future__ import annotations

from collections import namedtuple
from enum import Enum, unique
from typing import Dict, Optional

import aiohttp
import structlog

from diffusion.internal import protocol
from .credentials import Credentials

LOG = structlog.get_logger()

StateInfo = namedtuple("StateInfo", "description connected recovering closed")


@unique
class State(Enum):
    """ Connection state. """

    CONNECTING = StateInfo(
        "The session is establishing its initial connection.", False, False, False
    )
    CONNECTED_ACTIVE = StateInfo(
        "An active connection with the server has been established.",
        True,
        False,
        False,
    )
    RECOVERING_RECONNECT = StateInfo(
        "Connection with server has been lost and the session is attempting reconnection.",
        False,
        True,
        False,
    )
    CLOSED_BY_CLIENT = StateInfo(
        "The session has been closed by the client.", False, False, True
    )
    CLOSED_BY_SERVER = StateInfo(
        "The session has been closed (or rejected) by the server.", False, False, True
    )
    CLOSED_FAILED = StateInfo(
        "The session has lost its connection to a server and could not be recovered.",
        False,
        False,
        True,
    )

    def __getattr__(self, item):
        if item in StateInfo._fields:
            return getattr(self.value, item)
        return super().__getattribute__(item)


class Connection:
    """ Connection to the server. """

    def __init__(self, url: str, principal: str, credentials: Credentials):
        self.url = url
        self.principal = principal
        self.credentials = credentials
        self.protocol = protocol.Protocol
        self.state: State = State.CONNECTING
        self.response: Optional[protocol.ConnectionResponse] = None
        self._client: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None

    # TODO: implement reconnection (FB23157)
    async def connect(self, properties: Optional[Dict[str, str]] = None) -> None:
        """ Establishes a connection with the server. """
        if properties is None:
            properties = {}
        self.state = State.RECOVERING_RECONNECT if self.response else State.CONNECTING
        capabilities = (
            protocol.ConnectionParams.CAPABILITIES_ZLIB
            | protocol.ConnectionParams.CAPABILITIES_UNIFIED
        )
        params = protocol.ConnectionParams(
            version=self.protocol.VERSION,
            url=self.url,
            principal=self.principal,
            password=self.credentials.password,
            session_properties=properties,
            capabilities=capabilities,
        )
        LOG.debug("Connecting.", url=params.url, headers=params.headers)
        self._client = aiohttp.ClientSession()
        try:
            self._ws = await self._client.ws_connect(url=params.url, headers=params.headers)
        except aiohttp.ClientError as ex:
            LOG.warning("Connection error! Is the server online?", error=ex)
            raise protocol.ServerConnectionError from ex
        response = await self._ws.receive()
        try:
            self.response = self.protocol.parse_response(response.data)
        except protocol.ProtocolError:
            await self.close()
            raise
        else:
            self.state = State.CONNECTED_ACTIVE
            LOG.debug("Connected.", info=self.response)

    @property
    def is_connected(self):
        """ Checks the connection status. """
        return self.state.connected

    @property
    def is_reconnecting(self):
        """ Checks whether the connection is in process of reconnection. """
        return self.state.reconnecting

    @property
    def is_closed(self):
        """ Checks whether the connection is closed. """
        return self.state.closed

    async def send(self, data: bytes) -> None:
        """ Send bytes to the server. """
        LOG.debug("Sending bytes.", bytes=data)
        if not self.is_connected:
            raise protocol.ProtocolError("Not connected to Diffusion server!")
        await self._ws.send_bytes(data)  # type: ignore

    async def read_loop(self, session):
        """ Read the incoming messages and react to them. """
        async for msg in self._ws:
            if msg.type in (aiohttp.WSMsgType.BINARY, aiohttp.WSMsgType.TEXT):
                data = msg.data.encode() if msg.type == aiohttp.WSMsgType.TEXT else msg.data
                LOG.debug("Received bytes.", bytes=data)
                try:
                    await self.protocol.listen(session, data)
                except protocol.AbortMessageError:
                    LOG.info("Connection aborted by server.", server_bytes=data)
                    await self.close(State.CLOSED_BY_SERVER)
                    break
                except Exception as ex:
                    LOG.info("Error occurred on data receive.", data=data, error=ex)

    async def close(self, state=State.CLOSED_BY_CLIENT):
        """ Close the connection. """
        if self._ws:
            await self._ws.close()
        await self._client.close()
        self.state = state
        LOG.debug("Connection closed.", info=self.response)
        self.response = None
