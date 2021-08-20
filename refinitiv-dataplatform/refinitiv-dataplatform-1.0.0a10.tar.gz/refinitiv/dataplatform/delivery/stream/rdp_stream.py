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


class RDPStream(Stream):
    """this class is designed for the generic RDP stream.

        the following are the subscription message from the stream
    - ack message
    - response message
    - update message
    - alarm message
    """

    def __init__(self, session, api):
        Stream.__init__(self, session, api)

        #   store the RDP subscribe description
        self._service = None
        self._universe = None
        self._view = None
        self._parameters = None

        self._extended_params: dict = None

        #   store the future object when call the subscribe
        self._subscribe_future = None

    @property
    def service(self):
        return self._service

    @service.setter
    def service(self, val):
        self._service = val

    @property
    def universe(self):
        return self._universe

    @universe.setter
    def universe(self, val):
        self._universe = val

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, val):
        self._view = val

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, val):
        self._parameters = val

    @property
    def extended_params(self):
        return self._extended_params

    @extended_params.setter
    def extended_params(self, val):
        self._extended_params = val

    @property
    def protocol_name(self):
        return "RDP"

    ################################################
    #  methods to open and close asynchronously stream

    async def _do_open_async(self, **kwargs):
        """
        Open asynchronously the data stream
        """

        #   register the stream to session
        self._session._register_stream(self)

        #   waiting for stream connection is ready to connect
        assert self._session is not None
        assert callable(self._session.wait_for_streaming)
        result = await self._session.wait_for_streaming(self.api, self.protocol_name)

        #   check stream connection status
        if result:
            #   successfully connect to the stream, so send the subscription message

            #   initialize response future
            self._initialize_subscribe_response_future()

            #   get the subscription message
            subscription_message = self._get_subscription_request_message()
            self._session.log(
                5, "subscription message = {}".format(subscription_message)
            )

            #       send message to stream
            self._send(subscription_message)

            #   wait for subscribe response
            await self._wait_for_subscribe_response()

        else:
            #   failed to request the stream connection.
            self.state = StreamState.Closed
            self._session.log(
                1,
                "Start streaming failed. Set stream {} as {}".format(
                    self._stream_id, self._state
                ),
            )

        #   done
        return self.state

    async def _do_close_async(self, **kwargs):
        """
        Close the data stream

        example of close for generic RDP streaming
            {
                "streamID": "42",
                "method": "Close"
            }
        """
        self._session.debug(f"Close Stream subscription {self._stream_id}")

        #   initialize the unsubscribe response
        self._initialize_unsubscribe_response_future()

        #   close message
        close_message = {"streamID": f"{self._stream_id:d}", "method": "Close"}

        self._session.debug(
            f"Sent close subscription:\n"
            f'{json.dumps(close_message, sort_keys=True, indent=2, separators=(",", ":"))}'
        )
        self._send(close_message)

        #   cancel the previous subscribe response future
        if (
            self._subscribe_response_future is not None
            and not self._subscribe_response_future.done()
        ):
            #   valid future, so cancel it
            self._subscribe_response_future.cancel()

        #   wait for the unsubscribe response
        try:
            await asyncio.wait_for(
                self._wait_for_unsubscribe_response(),
                timeout=self._session.websocket_close_response_timeout_secs,
                loop=self._session._loop,
            )
        except asyncio.TimeoutError:
            self._session.warning(
                "WARNING!!! timeout occurred before received un-subsribed response."
            )

        #   unregister stream
        self._session._unregister_stream(self)

    def _do_pause(self):
        # do nothing
        pass

    def _do_resume(self):
        # do nothing
        pass

    ################################################
    #    methods to construct a RDP item subscription

    def _get_subscription_request_message(self):
        """build the subscription request message

        example of subscribe messages

            {
                "streamID": "42",
                "method": "Subscribe",
                "service": "analytics/bond/contract",
                "universe": [
                    {
                    "type": "swap",
                    "definition": {
                        "startDate": "2017-07-28T00:00:00Z",
                        "swapType": "Vanilla",
                        "tenor": "3Y"
                    }
                    }
                ],
                "view": [
                    "InstrumentDescription",
                    "ValuationDate",
                    "StartDate",
                    "EndDate",
                    "Calendar",
                    "FixedRate",
                    "PV01AmountInDealCcy",
                    "Duration",
                    "ModifiedDuration",
                    "ForwardCurveName",
                    "DiscountCurveName",
                    "ErrorMessage"
                ]
            }

        or

            {
                "streamID": "43",
                "method": "Subscribe",
                "service": "elektron/market-price",
                "universe": [
                    {
                    "name": "TRI.N"
                    }
                ]
            }

        or

            {
                "streamID": "1",
                "method": "Subscribe",
                "universe": [],
                "parameters": {
                    "universeType": "RIC"
                }
            }
        """

        #   get subscribe value if the override with extended_params is needed
        universe = (
            self.universe
            if self.extended_params is None or "universe" not in self.extended_params
            else self.extended_params["universe"]
        )
        service = (
            self.service
            if self.extended_params is None or "service" not in self.extended_params
            else self.extended_params["service"]
        )
        view = (
            self.view
            if self.extended_params is None or "view" not in self.extended_params
            else self.extended_params["view"]
        )

        #   parameters
        if self.extended_params is not None:
            if "parameters" not in self._extended_params:
                #   do not override
                parameters = self._parameters
            else:
                #   overrode parameters with extended_params
                if self.parameters is None:
                    #   use only the parameters in extended_params
                    parameters = self._extended_params["parameters"]
                else:
                    #   override parameters with extended parameters
                    parameters = dict(self._parameters)
                    parameters.update(self._extended_params["parameters"])
        else:
            #   do not override
            parameters = self._parameters

        #   construct subscription message
        subscription_message = {
            "streamID": f"{self._stream_id:d}",
            "method": "Subscribe",
            "universe": universe,
        }

        #   check for service and view
        if service is not None:
            #   add service into subscription message
            subscription_message["service"] = service

        #       view
        if view is not None:
            #   add view in to subscription message
            subscription_message["view"] = view

        #   parameters
        if parameters is not None:
            #   add parameters into the subscription message
            subscription_message["parameters"] = parameters

        #   done
        return subscription_message

    ###############################################################
    #    methods to subscribe/unsubscribe

    async def _subscribe_async(self):
        """
        Subscribe RDP stream.
        The subscription steps are waiting for stream to be ready and send the message to subscribe item.
        """
        self._session.log(
            5,
            "RDPStream.subscribe_async() - waiting for subscribe name = {}".format(
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
        open_message = self._get_subscription_request_message()
        self._session.log(5, "open message = {}".format(open_message))

        #       send message to stream
        self._send(open_message)

    ################################################
    #    callback functions

    def _on_status(self, status):
        """ callback for status """
        self._session.debug(
            f"Stream {self.stream_id} [{self.name}] - Receive status message {status}"
        )

    def _on_reconnect(
        self, failover_state, stream_state, data_state, state_code, state_text
    ):
        """ callback when the websocket connection in stream connection is reconnect """
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

    def _on_ack(self, ack):
        with self._stream_lock:
            if self._state is StreamState.Open:
                self._session.log(
                    1, f"Stream {self.stream_id} [{self.name}] - Receive ack {ack}"
                )

            #   get / update stream state
            state = ack.get("state", None)
            if state is not None:
                #   state contains in the ack message
                assert state is not None
                stream_state = state.get("stream", None)

                #   update state
                if stream_state == "Open":
                    #   received an open stream
                    self.state = StreamState.Open
                elif stream_state == "Closed":
                    #   received an closed stream
                    self.state = StreamState.Closed

                    #   check this ack is a response from unsubscribe message or not
                    if (
                        self._unsubscribe_response_future is not None
                        and not self._unsubscribe_response_future.done()
                    ):
                        #   this is a unsubscribe ack for this stream, so set the future to be True
                        self._unsubscribe_response_future.set_result(True)

                else:
                    #   unsupported state
                    self._session.log(
                        1,
                        f"Stream {self._stream_id} [{self._name}] - Receive unsupported stream state {stream_state}",
                    )

    def _on_response(self, response):
        with self._stream_lock:
            self._session.log(
                1,
                f"Stream {self.stream_id} [{self.name}] - Receive response {response}",
            )

            #   change state to be open if it's pending
            if self._state in [StreamState.Pending, StreamState.Closed]:
                self.state = StreamState.Open
                self._session.log(
                    1, "Set stream {} as {}".format(self.stream_id, self.state)
                )

            #   check this response is a first response of this subscribe item or not
            if (
                self._subscribe_response_future is not None
                and not self._subscribe_response_future.done()
            ):
                #   this is a first subscribe for this stream, so set the future to be True
                self._subscribe_response_future.set_result(True)

    def _on_update(self, update):
        with self._stream_lock:
            if self._state is StreamState.Open:
                self._session.log(
                    1,
                    f"Stream {self.stream_id} [{self.name}] - Receive update {update}",
                )

    def _on_alarm(self, message):
        with self._stream_lock:
            if self._state is StreamState.Open:
                self._session.log(
                    1,
                    f"Stream {self.stream_id} [{self.name}] - Receive alarm {message}",
                )
