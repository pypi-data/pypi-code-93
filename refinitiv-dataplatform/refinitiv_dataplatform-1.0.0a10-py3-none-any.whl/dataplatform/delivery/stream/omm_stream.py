# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

import asyncio
import json

###############################################################
#
#   REFINITIV IMPORTS
#

###############################################################
#
#   LOCAL IMPORTS
#


from .stream import Stream, StreamState


###############################################################
#
#   CLASS DEFINITIONS
#


class OMMStream(Stream):
    """This class is designed for the open message model (OMM) stream.

    The following are the subscription message from the stream (only the asterisk are now supported)
        - ack message
        - error message*
        - generic message
        - post message
        - refresh message*
        - status message*
        - update message*
        - complete message* (this is a special when the update message has a complete flag)
    """

    def __init__(self, session, api=None):
        #   set the default value when api is None to be 'streaming/pricing/main'
        Stream.__init__(self, session, "streaming/pricing/main" if api is None else api)

        #   store with_updates flags
        self._with_updates = True

        #   store the future object when call the subscribe
        self._subscribe_future = None

    @property
    def protocol_name(self):
        return "OMM"

    ###############################################################
    #   open/close asynchronous functions

    async def _do_open_async(self, **kwargs):
        """
        Open asynchronously the data stream
        """
        assert "with_updates" in kwargs
        #   store the with_updates flags
        self._with_updates = kwargs["with_updates"]

        from refinitiv.dataplatform.core.session import Session
        from refinitiv.dataplatform.errors import SessionError

        if self._session is None:
            raise AttributeError("Session is mandatory")

        if self._session.get_open_state() is Session.State.Closed:
            raise SessionError(-1, "Session must be opened")

        #   register the stream to session
        assert self._api is not None
        self._session._register_stream(self)

        # Wait for login successful before sending the request
        assert self._session is not None
        assert callable(self._session.wait_for_streaming)
        result = await self._session.wait_for_streaming(self.api, self.protocol_name)

        if result:
            #   successful connect to the stream, so send the subscription message

            #   initialize response future
            self._initialize_subscribe_response_future()

            #   send message to subscribe item
            #       construct open message
            open_message = self._get_open_stream_message()
            self._session.log(5, "open message = {}".format(open_message))

            #       send message to stream
            self._send(open_message)

            #   wait for subscribe response
            await self._wait_for_subscribe_response()

        else:
            #   failed to request the stream connection.
            self._session.log(
                1,
                "Start streaming failed. Set stream {} as {}".format(
                    self._stream_id, self._state
                ),
            )

        #   done
        return self.state

    async def _do_close_async(self):
        """
        Close the data stream
        """
        self._session.debug(f"Close Stream subscription {self._stream_id}")

        #   build a close message
        mp_req_json = {"ID": self._stream_id, "Type": "Close"}
        self._session.debug(
            f"Sent close subscription:\n"
            f'{json.dumps(mp_req_json, sort_keys=True, indent=2, separators=(",", ":"))}'
        )
        self._send(mp_req_json)

        #   cancel the previous subscribe response future
        self._subscribe_response_future and self._subscribe_response_future.cancel()

        #   un-register stream
        self._session._unregister_stream(self)

    def _do_pause(self):
        # do nothing
        pass

    def _do_resume(self):
        # do nothing
        pass

    ###############################################################
    #    methods to construct a omm item subscription

    def _get_open_stream_message(self):
        """ Construct and return a open message for this stream """
        assert self._with_updates is not None

        #   construct a open message
        open_message = {
            "ID": self._stream_id,
            "Domain": self._domain,
            "Streaming": self._with_updates,
        }
        #    for key option
        if self._key:
            open_message["Key"] = self._key
        else:
            open_message["Key"] = {}

        open_message["Key"]["Name"] = self._name

        #       for specific service option
        if self._service:
            open_message["Key"]["Service"] = self._service

        #       for specific view option
        if self._fields:
            open_message["View"] = self._fields

        #   done
        return open_message

    def _get_close_stream_message(self):
        """
        Construct and return a close message for this stream
        """

        #   construct a close message
        close_message = {"ID": self._stream_id, "Type": "Close"}

        #   done
        return close_message

    ###############################################################
    #    methods to subscribe/unsubscribe

    async def _subscribe_async(self):
        """
        Subscribe omm stream.
        The subscription steps are waiting for stream to be ready and send the message to subscribe item.
        """
        self._session.log(
            5,
            "OMMStream.subscribe_async() - waiting for subscribe name = {}".format(
                self._name
            ),
        )

        #   waiting for stream to be ready
        result = await self._session.wait_for_streaming_reconnection(
            self.api, self.protocol_name
        )

        #   check the reconnection result
        if not result:
            # failed to reconnection, so do nothing waiting for next reconnection
            self._session.debug(
                "WARNING!!! the reconnection is failed, so waiting for new reconnection."
            )
            return

        #   send message to subscribe item
        #       construct open message
        open_message = self._get_open_stream_message()
        self._session.log(5, "open message = {}".format(open_message))

        #       send message to stream
        self._send(open_message)

    ###############################################################
    #    callback functions

    def _on_reconnect(
        self, failover_state, stream_state, data_state, state_code, state_text
    ):
        """
        Callback when the websocket connection in stream connection is reconnect
        """
        self._session.debug(
            f"OMMStream._on_reconnect(failover_state={failover_state}, stream_state={stream_state}, data_state={data_state}, state_code={state_code}, state_text={state_text}))"
        )

        from .stream_connection import StreamConnection

        #   check the failover state for sent the new subscription item
        if failover_state == StreamConnection.FailoverState.FailoverCompleted:
            #   the stream connection failover is completed,
            #       so recover the stream by sent a new subscription item

            #   re-subscribe item
            if self._subscribe_future is None or self._subscribe_future.done():
                self._session.debug(
                    "      call subscribe_async() function.............."
                )

                #   do a subscription again
                self._subscribe_future = asyncio.run_coroutine_threadsafe(
                    self._subscribe_async(), loop=self._loop
                )

        #   do call the on_status callback
        #       build status message
        status_message = {
            "ID": self._stream_id,
            "Type": "Status",
            "Key": {"Name": self.name},
            "State": {
                "Stream": stream_state,
                "Data": data_state,
                "Code": state_code,
                "Text": state_text,
            },
        }

        #       call a status callback message
        self._on_status(status_message)

    ###############################################################
    #   callback functions when received messages

    def _on_refresh(self, message):
        with self._stream_lock:
            if self._state in [StreamState.Pending, StreamState.Closed]:
                self._session.log(
                    1,
                    f"Receive message {message} on stream {self._stream_id} [{self._name}]",
                )
                self.state = StreamState.Open
                self._session.log(
                    1, "Set stream {} as {}".format(self._stream_id, self._state)
                )

            #   check this refresh is a first refresh of this subscribe item or not
            #       it's possible that it's receiving a refresh message multiple time from server
            if (
                self._subscribe_response_future is not None
                and not self._subscribe_response_future.done()
            ):
                #   this is a first subscribe for this stream, so set the future to be True
                self._subscribe_response_future.set_result(True)

                #   set the stream state to open
                self.state = StreamState.Open

    def _on_update(self, update):
        with self._stream_lock:
            if self._state is StreamState.Open:
                self._session.log(
                    1,
                    f"Stream {self._stream_id} [{self._name}] - Receive update {update}",
                )

    def _on_status(self, status):
        """State : Conveys information about the health of the stream.
        Stream : The state of the event stream when using the request/response with interest paradigm.
            - Closed: Data is not available on this service and connection is not likely to become available,
            though the data might be available on another service or connection.
            - ClosedRecover: State is closed, however data can be recovered on this service and connection at a later time.
            - NonStreaming: The stream is closed and updated data is not delivered without a subsequent re-request.
            - Open: Data is streaming, as data changes it is sent to the stream.
            - Redirected: The current stream is closed and has new identifying information. The user can issue a new request
            for the data using the new message key data from the redirect message.
        """
        with self._stream_lock:
            self._session.log(
                1, f"Stream {self._stream_id} [{self._name}] - Receive status {status}"
            )

            #   check this error of this subscribe item
            #       it's possible that it's receiving a error instead of refresh message from server
            if (
                self._subscribe_response_future is not None
                and not self._subscribe_response_future.done()
            ):
                #   this is a first subscribe for this stream, so set the future to be True
                self._subscribe_response_future.set_result(True)

            #   get / update stream state
            state = status.get("State", None)
            assert state is not None
            stream_state = state.get("Stream", None)

            #   update state
            if stream_state == "Open":
                #   received an open stream
                self.state = StreamState.Open
            elif stream_state == "Closed":
                #   received an closed stream
                self.state = StreamState.Closed
            else:
                #   unsupported state
                self._session.log(
                    1,
                    f"Stream {self._stream_id} [{self._name}] - Receive unsupported stream state {stream_state}",
                )

    def _on_complete(self):
        with self._stream_lock:
            if self._state in [StreamState.Pending, StreamState.Open]:
                self._session.log(
                    1, f"Stream {self._stream_id} [{self._name}] - Receive complete"
                )

    def _on_error(self, error):
        with self._stream_lock:
            self._session.log(
                1, f"Stream {self._stream_id} [{self._name}] - Receive error {error}"
            )

            #   check this error of this subscribe item
            #       it's possible that it's receiving a error instead of refresh message from server
            if (
                self._subscribe_response_future is not None
                and not self._subscribe_response_future.done()
            ):
                #   this is a first subscribe for this stream, so set the future to be True
                self._subscribe_response_future.set_result(True)
