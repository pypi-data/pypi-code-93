# coding: utf8

__all__ = ["Stream", "StreamState"]

import abc
from enum import Enum, unique
from threading import Lock
from .openable import Openable

from .state import StreamState


@unique
class StreamEvent(Enum):
    STATUS = 0
    REFRESH = 1
    UPDATE = 2
    ERROR = 3
    COMPLETE = 4


class Stream(Openable, abc.ABC):
    """This class is designed to be a abstract class. this class manage subscription from websocket.
    It will have a notification message from session when received message from websocket.
    """

    def __init__(self, session, api=None):
        super().__init__()

        if session is None:
            raise AttributeError("Session is mandatory")

        #   store the streaming api of this stream
        self._api = api if api is not None else "streaming/pricing/main"

        self._stream_lock = Lock()
        self._stream_id = None
        self._session = session
        self._loop = session._loop

        self._name = None
        self._service = None
        self._fields = None
        self._domain = None
        self._key = None

        self._on = dict()

        #   store the subscribe response future
        #       this future is used for waiting until server response from subscribe request
        self._subscribe_response_future = None

        #   store the unsubscribe response future
        #       this future is used for waiting until server response from unsubscribe request
        self._unsubscribe_response_future = None

    @property
    def stream_id(self):
        return self._stream_id

    @stream_id.setter
    def stream_id(self, val):
        self._stream_id = val

    @property
    def api(self):
        return self._api

    @property
    def name(self):
        return self._name

    @property
    @abc.abstractmethod
    def protocol_name(self):
        pass

    def _initialize_subscribe_response_future(self):
        """ Initialize subscribe response future """

        #   check currently subscribe response future
        if (
            self._subscribe_response_future is not None
            and not self._subscribe_response_future.done()
        ):
            #   cancel the previous subscribe response future
            self._subscribe_response_future.cancel()

        #   create the subscribe response future
        self._subscribe_response_future = self._loop.create_future()

    def _initialize_unsubscribe_response_future(self):
        """ Initialize unsubscribe response future """

        #   check currently unsubscribe response future
        if (
            self._unsubscribe_response_future is not None
            and not self._unsubscribe_response_future.done()
        ):
            #   cancel the previous subscribe response future
            self._loop.call_soon_threadsafe(self._unsubscribe_response_future.cancel)

        #   create the subscribe response future
        self._unsubscribe_response_future = self._loop.create_future()

    async def _wait_for_subscribe_response(self):
        """ waiting for a subscribe response """
        await self._subscribe_response_future

    async def _wait_for_unsubscribe_response(self):
        """ waiting for an unsubscribe response """
        await self._unsubscribe_response_future

    def _send(self, message):
        """ Send a message to the websocket server """
        self._session.debug(
            f"Stream("
            f"id={self._stream_id}, name={self._name}, api={self.api})"
            f".send(message = {message})"
        )
        self._session.send(self.api, message)

    ################################################
    #    forward function
    def on(self, event: StreamEvent, message):
        if event in self._on:
            self._on(event, message)

    ################################################
    #    callback functions

    @abc.abstractmethod
    def _on_status(self, status):
        """ callback for status """
        pass

    @abc.abstractmethod
    def _on_reconnect(
        self, failover_state, stream_state, data_state, state_code, state_text
    ):
        """ Callback when the websocket connection in stream connection is reconnect """
        pass

    def _on_stream_state(self, state):
        self.state = state
