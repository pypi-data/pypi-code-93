# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

import asyncio
import functools
import json
import threading
import time

###############################################################
#
#   REFINITIV IMPORTS
#

from .stream_connection import StreamConnection


###############################################################
#
#   LOCAL IMPORTS
#


###############################################################
#
#   CLASS DEFINITIONS
#


class OMMStreamConnection(StreamConnection):
    """ This class is designed for handling the OMM connect via websocket protocol """

    def __init__(self, *args, **kwargs):
        StreamConnection.__init__(self, *args, **kwargs)

        #   check websocket connection
        self._last_check_websocket_connection_time = None
        self._check_websocket_connection_timer = None
        self._check_response_pong_timer = None

        #   login failed future
        self._login_failed_future = None

    #############################################################
    #   construct the login/close message

    def _get_login_message(self):
        """The function is used to build the login message (included authentication).

        It is designed to be override by child class that can define own login message for difference kind of connect.
            ie. Open Message Model (OMM)
                {
                    "Domain":"Login",
                    "ID":1,
                    "Key":{
                        "Elements":{
                        "ApplicationId":"555",
                        "AuthenticationToken":"aBcDeFgHiJkLmNoPqRsTuVwXyZ",
                        "Position":"127.0.0.1"
                        },
                        "NameType":"AuthnToken"
                    }
                }

        Returns
        -------
        string
            the login message from client to server
        """

        #   request and store the login stream event id from session
        self._login_stream_event_id = self._session._get_new_id()

        #   build platform OMM login message
        key_data = self._session.get_omm_login_message_key_data()
        assert key_data is not None
        login_message = {
            "Domain": "Login",
            "ID": self._login_stream_event_id,
            "Key": key_data,
        }

        # done, return login message
        return login_message

    def _get_close_message(self):
        """This function is used to build the close message.

        It is designed to be override by child class that can define own close message for difference kind of connect.
            ie. Open Message Model (OMM)
                {
                    "Domain":"Login",
                    "ID":1,
                    "Type": "Close"
                }

        Returns
        -------
        string
            the close message from client to server
        """

        #   build platform OMM close message
        close_message = {
            "Domain": "Login",
            "ID": self._login_stream_event_id,
            "Type": "Close",
        }

        # done, return close message
        return close_message

    def _get_auth_message(self):
        """This function is used to build the authentication message.
        Note that the message is almost identical to login message but the id is the current id.
            Open Message Model (OMM)
            {
                "Domain":"Login",
                "ID":1,
                "Key":{
                    "Elements":{
                        "ApplicationId":"555",
                        "AuthenticationToken":"aBcDeFgHiJkLmNoPqRsTuVwXyZ",
                        "Position":"127.0.0.1"
                        },
                    "NameType":"AuthnToken"
                }
            }
        """

        #   build platform OMM authentication message
        key_data = self._session.get_omm_login_message_key_data()
        assert key_data is not None
        auth_message = {
            "Domain": "Login",
            "ID": self._login_stream_event_id,
            "Key": key_data,
        }

        # done, return authentication message
        return auth_message

    async def __send_and_wait_for_login_or_authentication_message(self, auth_message):
        """This function is designed for send the login or authentication message
            then wait for the response of the sent message (login/authentication)

        This function will re-initialize the login future.
        The future object will be triggered and set it to be true when get the response.

        NOTE that the login and authentication cannot distinguish yet.
        """

        #   initialize login future
        self._initialize_login_future()

        #   set the future object to wait for this login response
        assert self._login_response_future is not None
        assert not self._login_response_future.done()
        assert not self._login_response_future.cancelled()

        #   send a login message to the server via websocket
        self.debug(
            f"Sending the authentication message. url={self._connection_config.url}, message={auth_message}"
        )
        with self._ws_lock:
            self.send(auth_message)

        #   wait for process login response
        result = await self._wait_and_process_login_response_message()

        #   done
        return result

    #############################################################
    #  process authentication token update

    def _set_stream_authentication_token(self, authentication_token):
        """ Re-authenticate to websocket server """
        self._session.debug("OMMStreamConnection._set_stream_authentication_token()")

        #   do re-authentication to websocket server

        #   get authentication message
        auth_message = self._get_auth_message()
        self.debug(
            f"OMMStreamConnection.authentication_token() - authentication message = {auth_message}"
        )

        #   send the authentication message
        self.info(
            f"Send new authentication message to websocket[{self._login_stream_event_id}] - {self._login_stream_event_id}"
        )

        #   send and wait for a response form authentication message
        # result = await self.__send_and_wait_for_login_or_authentication_message(auth_message)
        self.send(auth_message)

    #############################################################
    #   send messages

    def _pong(self):
        """ Send pong message to websocket server """
        self._session.debug("    ... sending pong response")

        #   construct and send pong message
        pong_message = {"Type": "Pong"}
        self.send(pong_message)

    def _ping(self):
        """ Send ping message to websocket server """
        self._session.debug("    ... sending ping response")

        #   construct and send ping message
        ping_message = {"Type": "Ping"}
        self.send(ping_message)

        #   store last ping message to websocket api
        self._last_ping_message_time = time.time()

    #############################################################
    #   process response messages

    def _on_messages(self, messages):
        """Received response messages callback function from websocket.
        This function designed to be extract websocket raw data to be a object messages ie. json format
            and call _process_response_message method to process each massage.
        """

        #   extract the raw data into json format
        try:
            messages_json = json.loads(messages)
        except UnicodeDecodeError:
            self._session.debug(
                f"OMMStreamConnection._on_message: JSONDecodeError with message={messages[:50]})"
            )
            messages = "".join(map(chr, [byte for byte in bytearray(messages)]))
            messages_json = json.loads(messages)

        #   loop over all messages and _process_response_message for each messages
        for message in messages_json:
            #   process a single response message from websocket
            self._process_response_message(message)

    # def _update_last_response_message(self):
    #     #   store the last message received from server
    #     self._last_received_messages_time = time.time()

    #     if self._check_websocket_connection_timer is not None:
    #         #   cancel old check websocket connection timer
    #         self._check_websocket_connection_timer.cancel()

    #     #   create check websocket connection timer
    #     self._check_websocket_connection_timer = threading.Timer(self._idle_timeout_secs,
    #                                                              self._check_websocket_connection)
    #     self._check_websocket_connection_timer.name = 'StreamConnectionTimer - check websocket connection'
    #     self._check_websocket_connection_timer.start()

    # def _check_websocket_connection(self):
    #     """ Check websocket connection """

    #     #   update last time for check websocket connection
    #     self._last_check_websocket_connection_time = time.time()

    #     #   do check with last response from websocket
    #     if self._last_received_messages_time + self._idle_timeout_secs < self._last_check_websocket_connection_time:
    #         #   still receiving response messages from websocket in proper time
    #         return

    #     #   don't receive any response messages from websocket for a long period
    #     #       so send the ping to websocket for checking a connection

    #     #   need to send the ping to websocket server
    #     self._ping()

    #     #   add timer for check received response pong for server
    #     if self._check_response_pong_timer is not None:
    #         #   cancel the old check response pong
    #         self._check_response_pong_timer.cancel()

    #     #   create new timer for check pong from server
    #     self._check_response_pong_timer = threading.Timer(self._idle_timeout_secs, self._check_pong_response_cb)

    # def _check_pong_response_cb(self):
    #     """ Check the pong response from server """

    #     #   check for timeout
    #     if self._last_pong_message_time + self._ping_pong_timeout_secs > time.time():
    #         #   timeout for pong response from server, so close the websocket
    #         self._websocket.close()

    def _process_response_message(self, message):
        """Process a single response message from websocket server.
        It is designed to be override by child class that can define how to handle response message.

        This is a OMM content message including (only the asterisk are now supported)
            - ack message
            - close*
            - error message*
            - generic message
            - ping and pong*
            - post message
            - refresh message*
            - request message*
            - status message*
            - update message*
        """
        self._session.debug(
            f"OMMStreamConnection._process_response_message(message={message})"
        )

        # warning TEMPORARY DISABLE
        # #   update response message is received
        # self._update_last_response_message()

        #   filter by the message id, type and domain to process
        #       id
        message_id = message.get("ID")
        #       type
        message_type = message.get("Type")
        assert message_type is not None
        #       domain
        message_domain = message.get("Domain")

        if message_domain == "Login":
            #######################################################
            #   login domain
            #   call the process login message
            result = self._process_login_response_message(message)

            #   check the type of login message
            #       do check this is a login that requested and waiting or not?
            # warning :: UNCOMMENT ME :: DESKTOP SESSION PROXY RETURN DIFFERENCE FROM LOGIN MESSAGE ID REQUESTED
            # #if message_type == 'Refresh' and message_id == self._login_stream_event_id and not self._login_response_future.done():
            # if message_type == 'Refresh':
            # #   matched the login message that requested, set the future to be done and pass the login response message

            #     # #   trigger received login message
            #     # self._on_receive_login_message(result)
            if message_type == "Refresh" and not self._login_response_future.done():
                #   matched the login message that requested, set the future to be done and pass the login response message
                self._on_receive_login_message(result)

                #   ready for a connection
                if result and not self._ready_future.done():
                    self._on_ready()

                #   check it doesn't completed by _ws_login_failed function
                if (
                    self._reconnect_state
                    and self._reconnect_state != self.FailoverState.FailoverCompleted
                ):
                    #   call the completed reconnection
                    self._completed_ws_reconnection()

            #   done
            return
        elif message_domain == "Source":
            #######################################################
            #   Source domain
            #   call the process service message
            self._process_service_response_message(message_id, message_type, message)
            return

        #######################################################
        #   process by message type

        #   filter by message types
        if message_type == "Refresh":
            #   call process refresh message
            self._process_refresh_message(message_id, message)
        elif message_type == "Update":
            #   call process update message
            self._process_update_message(message_id, message)
        elif message_type == "Status":
            #   call process status message
            self._process_status_message(message_id, message)
        elif message_type == "Error":
            #   call process error message
            self._process_error_message(message_id, message)
        elif message_type == "Ping":
            #   sent the pong message back to websocket server
            self._pong()
        elif message_type == "Pong":
            self._last_pong_message_time = time.time()
        else:
            #   unsupported message type
            self._session.debug(
                "WARNING!!! unsupported message type {}. message = {}".format(
                    message_type, message
                )
            )

        #   done

    #############################################################
    #   wait and process login/close message from websocket
    #       note that this overriding from parent StreamConnection class

    async def _wait_and_process_login_response_message(self):
        """Wait and process the login (may include authentication) response message from websocket server
        This function will wait for login response all call the _process_login_response_message method

        Returns
        -------
        boolean
            True if the process login message success otherwise False
        """

        self._session.debug("Wait for login response.")
        #   wait for login response
        await self._login_response_future
        self._session.debug("Login response was received.")

        #   done
        #       cleanup login response future
        self._login_response_future = None

        #   done, return success
        return True

    async def _wait_and_process_close_response_message(self):
        """Wait and process the close response message from websocket server
        This function will wait for close response all call the _process_close_response_message method
            Open Message Model (OMM) close message doesn't has response, so do not waiting the close response message

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
    #   process login response messages
    #       note that this overriding from parent StreamConnection class

    def _process_login_response_message(self, login_response_message):
        """Process the login (may include authentication) response message from websocket server
        It is designed to be override by child class that can define handle own login message for difference kind of connect.
            ie. Open Message Model (OMM)
                [
                    {
                        "Domain":"Login",
                        "Elements":{
                        "MaxMsgSize":61440,
                        "PingTimeout":30
                        },
                        "ID":1,
                        "Key":{
                        "Elements":{
                            "AllowSuspectData":1,
                            "ApplicationId":"555",
                            "ApplicationName":"ADS",
                            "AuthenticationErrorCode":0,
                            "AuthenticationErrorText":"Success",
                            "Position":"127.0.0.1",
                            "ProvidePermissionExpressions":1,
                            "ProvidePermissionProfile":0,
                            "SingleOpen":1,
                            "SupportBatchRequests":7,
                            "SupportEnhancedSymbolList":1,
                            "SupportOMMPost":1,
                            "SupportOptimizedPauseResume":1,
                            "SupportPauseResume":1,
                            "SupportStandby":0,
                            "SupportViewRequests":1
                        },
                        "Name":"user"
                        },
                        "State":{
                        "Data":"Ok",
                        "Stream":"Open",
                        "Text":"Login accepted by host."
                        },
                        "Type":"Refresh"
                    }
                ]
        Parameters
        ----------
        login_response_message : dict
            the login message from websocket server

        Returns
        -------
        boolean
            True if the process login message success otherwise False
        """
        #   extract data from response message
        response_id = login_response_message.get("ID")
        if response_id == self._login_stream_event_id:
            #   the response id match with requested login id
            self._session.debug(f"Received login response for login id {response_id}")
        else:
            #   the response login id is difference from requested login id
            self._session.debug(
                f"Received login response for id {response_id} different than login id {self._login_stream_event_id}"
            )

        # warning :: UNCOMMENT ME :: DESKTOP SESSION PROXY RETURN DIFFERENCE FROM LOGIN MESSAGE ID REQUESTED
        #     #   do nothing
        #     return False

        # assert(response_id == self._login_stream_event_id)

        # #   trigger received login message
        # self._on_receive_login_message(True)

        #   check the response login state
        state_dict = login_response_message.get("State")
        assert state_dict is not None

        #       data
        state_data = state_dict.get("Data")
        #       stream
        state_stream = state_dict.get("Stream")
        #       text
        state_text = state_dict.get("Text")

        #   validate the login
        if state_stream == "Open" and state_data == "Ok":
            #   successfully login and stream is ready

            #   extract ads information about ping/pong timeout and maximum message size
            element_dict = login_response_message.get("Elements")
            assert element_dict is not None

            #   ADS information
            #       ping/pong timeout
            self._ping_pong_timeout_secs = element_dict.get("PingTimeout")
            # assert self._ping_pong_timeout_secs
            #       max message size
            self._max_message_size_bytes = element_dict.get("MaxMsgSize")
            # assert self._max_message_size_bytes

            #   change stream connection state to open
            self._state = StreamConnection.State.OPEN
            self.info(f"Login to websocket {self._connection_config.url} successful")

            #   call a on_event callback function
            self._session_on_event_cb(
                self._streaming_session_id,
                self._session.EventCode.StreamConnected,
                state_text,
                stream_connection_name=self._connection_name,
            )

            #   done, successful
            return True

        else:
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
    #   process Source message

    def _process_service_response_message(
        self, message_id, message_type, service_message
    ):
        #   filter by message types
        if message_type == "Refresh":
            #   call process refresh message
            self._process_refresh_message(message_id, service_message)
        elif message_type == "Update":
            #   call process update message
            self._process_update_message(message_id, service_message)
        elif message_type == "Status":
            #   call process status message
            self._process_status_message(message_id, service_message)
        elif message_type == "Error":
            #   call process error message
            self._process_error_message(message_id, service_message)

    #############################################################
    #   process Dictionary message
    #   Dictionary response message are similar to common stream response

    #############################################################
    #   process response message by types

    def _process_refresh_message(self, stream_event_id, message):
        """Process a refresh response message from websocket server
        The refresh may cause the on_complete event, check and call the on_complete callback if it's necessary
        """
        #   get list of subscribed streams
        subscription_streams = self._session.get_subscription_streams(stream_event_id)
        if subscription_streams is None or len(subscription_streams) == 0:
            #   no stream subscribed to this stream event id
            self._session.debug(
                "WARNING!!! Receive refresh message for unknown subscription {}".format(
                    stream_event_id
                )
            )

        #  loop over all stream and call the refresh message callback function
        for stream in subscription_streams:
            #   call the refresh callback function
            assert hasattr(stream, "_on_refresh")
            self._loop.call_soon_threadsafe(
                functools.partial(stream._on_refresh, message)
            )

            #   check for complete message, to call the on_complete callback
            #       The complete attribute Indicates that the payload data in the response is complete.
            #   Some domain models require a single response with payload data;
            #   others allow multi-part responses of payload data that will have this flag set in the last message.
            #   If absent, Complete defaults to true.
            refresh_complete = message.get("Complete", True)
            if refresh_complete is not None and refresh_complete == True:
                #   it indicate this is a completed message, so call the on_complete callback function
                assert hasattr(stream, "_on_complete")
                self._loop.call_soon_threadsafe(functools.partial(stream._on_complete))

    def _process_update_message(self, stream_event_id, message):
        """ Process update response message from websocket server """
        #   get list of subscribed streams
        subscription_streams = self._session.get_subscription_streams(stream_event_id)
        if subscription_streams is None or len(subscription_streams) == 0:
            #   no stream subscribed to this stream event id
            self._session.debug(
                "WARNING!!! Receive update message for unknown subscription {}".format(
                    stream_event_id
                )
            )

        #  loop over all stream and call the update message callback function
        for stream in subscription_streams:
            #   call the update callback function
            assert hasattr(stream, "_on_update")
            self._loop.call_soon_threadsafe(
                functools.partial(stream._on_update, message)
            )

    def _process_status_message(self, stream_event_id, message):
        """ Process a status message from websocket server """
        #   get list of subscribed streams
        subscription_streams = self._session.get_subscription_streams(stream_event_id)
        if subscription_streams is None or len(subscription_streams) == 0:
            #   no stream subscribed to this stream event id
            self._session.debug(
                "WARNING!!! Receive status message for unknown subscription {}".format(
                    stream_event_id
                )
            )

        #  loop over all stream and call the status message callback function
        for stream in subscription_streams:
            #   call the status callback function
            assert hasattr(stream, "_on_status")
            self._loop.call_soon_threadsafe(
                functools.partial(stream._on_status, message)
            )

    def _process_error_message(self, stream_event_id, message):
        """ Process error response message from websocket server """
        #   get list of subscribed streams
        subscription_streams = self._session.get_subscription_streams(stream_event_id)
        if subscription_streams is None or len(subscription_streams) == 0:
            #   no stream subscribed to this stream event id
            self._session.debug(
                "WARNING!!! Receive error message for unknown subscription {}".format(
                    stream_event_id
                )
            )

        #  loop over all stream and call the error message callback function
        for stream in subscription_streams:
            #   call the error callback function
            assert hasattr(stream, "_on_error")
            self._loop.call_soon_threadsafe(
                functools.partial(stream._on_error, message)
            )
