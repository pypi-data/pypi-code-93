# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#
import asyncio
import functools
import json
import logging

###############################################################
#
#   REFINITIV IMPORTS
#

###############################################################
#
#   LOCAL IMPORTS
#

from .stream_connection import StreamConnection


###############################################################
#
#   CLASS DEFINITIONS
#


class RDPStreamConnection(StreamConnection):
    """ this class is designed for handling the generic RDP streaming contect via websocket protocol """

    def __init__(self, *args, **kwargs):
        StreamConnection.__init__(self, *args, **kwargs)

        #   login future object
        self._login_failed_future = None

    #############################################################
    #   construct the login/close message

    def _get_login_message(self):
        """the function is used to build the login message (included authentication).
        it is designed to be override by child class that can define own login message for difference kind of connect.
            ie. generic RDP streaming

            platform session
                {
                    "streamID": "42",
                    "method": "Auth",
                    "token": <token returned by oauth authentication>,
                }

            desktop session
                {
                    "streamID": "42",
                    "method": "Auth",
                    "appKey": <app key>,
                }



        Parameters
        ----------

        Returns
        -------
        string
            the login message from client to server
        """

        #   request and store the login stream event id from session
        self._login_stream_event_id = self._session._get_new_id()

        #   build platform generic RDP streaming login message
        login_message = self._session.get_rdp_login_message(self._login_stream_event_id)

        # done, return login message
        return login_message

    def _get_close_message(self):
        """this function is used to build the close message.
        it is designed to be override by child class that can define own close message for difference kind of connect.

        Parameters
        ----------

        Returns
        -------
        string
            the close message from client to server
        """
        pass

    #############################################################
    #  wait and process login/close message from websocket

    async def _wait_and_process_login_response_message(self):
        """wait and process the login (may include authentication) response message from websocket server
        this function will wait for login response all call the _process_login_response_message method

        Parameters
        ----------

        Returns
        -------
        boolean
            True if the process login message success otherwise False
        """

        #   wait for login response
        await self._login_response_future

        #   done
        #       cleanup login response future
        self._login_response_future = None

        #   done, return success
        return True

    async def _wait_and_process_close_response_message(self):
        """wait and process the close response message from websocket server
        this function will wait for close response all call the _process_close_response_message method

        Parameters
        ----------

        Returns
        -------
        boolean
            True if the process close message success otherwise False
        """
        #   cleanup close response future
        self._close_response_future = None

        #   done, return success
        return True

    #############################################################
    #  process authentication token update

    def _set_stream_authentication_token(self, authentication_token):
        """ re-authenticate to websocket server """
        self._session.debug("RDPStreamConnection._set_stream_authentication_token()")

        #   do re-authentication to websocket server

        #   get authentication message
        auth_message = self._session.get_rdp_login_message(self._login_stream_event_id)
        self.debug(
            f"RDPStreamConnection.authentication_token() - authentication message = {auth_message}"
        )

        #   send the authentication message
        self.info(
            f"Send new authentication message to websocket[{self._login_stream_event_id}] - {self._login_stream_event_id}"
        )

        #   send and wait for a response form authentication message
        self.send(auth_message)

    ##############################################################
    #   process response messages

    def _on_messages(self, messages):
        """received messages callback function from websocket.
        this function designed to be extract websocket raw data to be a object messages ie. json format.
            and call _process_response_message method to process each massage.
        """
        self._session.log(
            logging.DEBUG,
            "RDPStreamConnection._on_messages(messages={})".format(messages),
        )

        #   extract the raw data into json format
        messages_json = json.loads(messages)

        #   loop over all messages and _process_response_message for each messages
        for message in messages_json:
            #   process a single response message from websocket
            self._process_message(message)

    def _process_message(self, message):
        """process a single response message from websocket server.
        it is designed to be override by child class that can define how to handle response message.

                 the following are types of message from the RDP WebSocket protocol/
            - ack message
            - response message
            - update message
            - alarm message
        """
        self._session.debug(
            "RDPStreamConnection._process_message(message={})".format(message)
        )

        #   filter by the message id and type to process
        #       id
        message_id_str = message.get("streamID")
        if message_id_str:
            #   valid message id string
            #           convert to int
            assert isinstance(message_id_str, str)
            assert message_id_str.isdigit()
            message_id = int(message_id_str)
        else:
            #   empty message id string
            message_id = None

        #       type
        assert "type" in message
        message_type = message.get("type")

        #######################################################
        #   login ack response

        #   check the stream id for login response
        if message_id is not None and message_id == self._login_stream_event_id:
            #   this is a login response
            #   call the process login message
            result = self._process_login_response_message(message_id, message)

            #  check the type of login message
            if (
                message_type == "Ack"
                and message_id == self._login_stream_event_id
                and not self._login_response_future.done()
            ):
                #   matched the login message that requested, set the future to be done and pass the login response message
                self._on_receive_login_message(result)

                #   ready for a connection
                if result and not self._ready_future.done():
                    self._on_ready()

            #   done
            return

        #######################################################
        #   process by message type

        #   filter by message types
        if message_type == "Ack":
            #   call process ack message
            self._process_ack_message(message_id, message)
        elif message_type == "Response":
            #   call process response message
            self._process_response_message(message_id, message)
        elif message_type == "Update":
            #   call process update message
            self._process_update_message(message_id, message)
        elif message_type == "Alarm":
            #   call process alarm message
            self._process_alarm_message(message_id, message)
        # warning ignore the heartbeat message
        elif message_type == "Heartbeat":
            #   ignore heartbeat message
            self._session.debug(
                "#WARNING do nothing after received heartbeat from server."
            )
        else:
            #   unsupported message type
            self._session.debug(
                "WARNING!!! unsupported message type {}. message = {}".format(
                    message_type, message
                )
            )

        #   done

    #############################################################
    #   handle the login/close response message

    def _process_login_response_message(self, stream_event_id, login_response_message):
        """process the login (may include authentication) response message from websocket server
        it is designed to be override by child class that can define handle own login message for difference kind of connect.
            ie. generic RDP streaming
                [
                    {
                        "streamID": "42",
                        "type": "Ack",
                        "state": {
                            "code": 200,
                            "message": "Ok"
                            }
                    }
                ]
        Parameters
        ----------
        stream_event_id : string

        login_response_message : string
            the close message from websocket server

        Returns
        -------
        boolean
            True if the process close message success otherwise False
        """
        #   extract data from response message
        if stream_event_id == self._login_stream_event_id:
            #   the response id match with requested login id
            self._session.debug(
                f"Received login response for login id {stream_event_id}"
            )
        else:
            #   the response login id is difference from requested login id
            self._session.debug(
                f"Received login response for id {stream_event_id} different than login id {self._login_stream_event_id}"
            )

            #   do nothing
            return False

        assert stream_event_id == self._login_stream_event_id

        #   check the response login state
        state_dict = login_response_message.get("state")
        assert state_dict is not None

        #       code
        state_code = state_dict.get("code")
        #       message
        state_message = state_dict.get("message")

        #   validate the login
        if state_code == 200:  # and state_message == 'Ok':
            #   successfully login and stream is ready

            #   change stream connection state to open
            self._state = StreamConnection.State.OPEN
            self.info(f"Login to websocket {self._connection_config.url} successful")

            #   call a on_event callback function
            self._session_on_event_cb(
                self._streaming_session_id,
                self._session.EventCode.StreamConnected,
                state_message,
                stream_connection_name=self._connection_name,
            )

            #   done, successful
            return True

        else:
            #   error response from login request

            #   error response from login request
            self.debug("#WARNING!!! login has been failed...........")

            if self._login_failed_future is None or self._login_failed_future.done():
                #   call the websocket login callback.
                self.debug(
                    "        requesting the new token to login to the WebSocket."
                )
                self._ws_login_failed()

            #   done, unsuccessful login to websocket
            return False

    #############################################################
    #   process response message by types

    def _process_ack_message(self, stream_event_id, message):
        """process a ack message from websocket server.
            this message will forward to all subscribed steams by _on_ack callback function.

        example of ack message
            [
                {
                    "streamID": "44",
                    "type": "Ack",
                    "state": {
                        "code": 200,
                        "text": "item updated"
                        }
                }
            ]
        """

        #   check stream id
        if stream_event_id is not None:
            #   valid stream id, so get the subscribed stream

            #   get list of subscribed streams
            subscription_streams = self._session.get_subscription_streams(
                stream_event_id
            )
            if subscription_streams is None or len(subscription_streams) == 0:
                #   no stream subscribed to this stream event id
                self._session.debug(
                    "WARNING!!! Receive ack message for unknown subscription {}".format(
                        stream_event_id
                    )
                )
                #   done
                return

        else:
            #   invalid stream event id, so it doesn't have any subscribed stream
            return

        #  loop over all stream and call the ack message callback function
        for stream in subscription_streams:
            #   call the ack callback function
            assert hasattr(stream, "_on_ack")
            self._loop.call_soon_threadsafe(functools.partial(stream._on_ack, message))

    def _process_response_message(self, stream_event_id, message):
        """process a response message from websocket server.
        this message will forward to all subscribed steams by _on_response callback function.
        """
        #   get list of subscribed streams
        subscription_streams = self._session.get_subscription_streams(stream_event_id)
        if subscription_streams is None or len(subscription_streams) == 0:
            #   no stream subscribed to this stream event id
            self._session.debug(
                "WARNING!!! Receive response message for unknown subscription {}".format(
                    stream_event_id
                )
            )
            #   done
            return

        #  loop over all stream and call the response message callback function
        for stream in subscription_streams:
            #   call the response callback function
            assert hasattr(stream, "_on_response")
            self._loop.call_soon_threadsafe(
                functools.partial(stream._on_response, message)
            )

    def _process_update_message(self, stream_event_id, message):
        """process a update message from websocket server.
        this message will forward to all subscribed steams by _on_update callback function.
        """
        #   get list of subscribed streams
        subscription_streams = self._session.get_subscription_streams(stream_event_id)
        if subscription_streams is None or len(subscription_streams) == 0:
            #   no stream subscribed to this stream event id
            self._session.debug(
                "WARNING!!! Receive update message for unknown subscription {}".format(
                    stream_event_id
                )
            )
            #   done
            return

        #  loop over all stream and call the update message callback function
        for stream in subscription_streams:
            #   call the update callback function
            assert hasattr(stream, "_on_update")
            self._loop.call_soon_threadsafe(
                functools.partial(stream._on_update, message)
            )

    def _process_alarm_message(self, stream_event_id, message):
        """process a alarm message from websocket server.
        this message will forward to all subscribed steams by _on_alrm callback function.
        """
        #   check stream id
        if stream_event_id is not None:
            #   valid stream id, so get the subscribed stream

            #   get list of subscribed streams
            subscription_streams = self._session.get_subscription_streams(
                stream_event_id
            )
            if subscription_streams is None or len(subscription_streams) == 0:
                #   no stream subscribed to this stream event id
                self._session.debug(
                    "WARNING!!! Receive alarm message for unknown subscription {}".format(
                        stream_event_id
                    )
                )
                #   done
                return

        else:
            #   invalid stream event id, so it doesn't have any subscribed stream
            return

        #  loop over all stream and call the alarm message callback function
        for stream in subscription_streams:
            #   call the alarm callback function
            assert hasattr(stream, "_on_alarm")
            self._loop.call_soon_threadsafe(
                functools.partial(stream._on_alarm, message)
            )
