# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

import collections

import time

import asyncio

import httpx

import functools

import threading

import requests_async as requests

###############################################################
#
#   REFINITIV IMPORTS
#

###############################################################
#
#   LOCAL IMPORTS
#

from .grant_password import GrantPassword
from .grant_refresh import GrantRefreshToken

###############################################################
#
#   CLASS DEFINITIONS
#


class AuthenticationTokenHandlerThread(threading.Thread):
    """this class is designed for handling the oauth token for RDP platform connection.
    the following are things handling by this class
        - request an access token.
        - request to refresh an access token.
        - forward the new access token to the session (the session itself will be forward to all active stream connection)
    only when the server_mode is True
        - if the token is expired and cannot refresh, it will do the request the token by password (if it's possible)
    """

    AuthenticationTokenInformation = collections.namedtuple(
        "AuthenticationTokenInformation",
        ["access_token", "expires_in", "refresh_token", "scope", "token_type"],
    )

    def __init__(
        self,
        session,
        grant,
        authentication_endpoint_url: str,
        server_mode: bool = None,
        take_exclusive_sign_on_control=None,
    ):
        threading.Thread.__init__(self, name="AuthenticationTokenHandlerThread")

        self._session = session
        self._grant = grant

        #   event loop for authentication token handler
        self._loop = None

        #   store the endpoint for an authentication (last requested token)
        self._authentication_endpoint_url = authentication_endpoint_url

        #   set the default for server mode
        self._server_mode = False if server_mode is None else server_mode
        if self._server_mode and not self.is_passsword_grant():
            #   server mode is disabled because grant type is not a password grant
            self._session.warning(
                "WARNING!!! server-mode is disabled because the grant type is not a password grant."
            )
        self._session.debug(f"        server-mode : {self._server_mode}")

        #   set the default for exclusive sign on control
        self._take_exclusive_sign_on_control = (
            True if take_exclusive_sign_on_control is None else False
        )

        #   events
        self._request_new_authentication_token_event = threading.Event()
        self._start_event = threading.Event()
        self._stop_event = threading.Event()
        self._ready = threading.Event()
        self._error = threading.Event()

        #   exception
        self._last_exception = None

        #   store the request token information for calculating the delay
        self._token_expires_in_secs = None
        self._token_requested_time = None

    @property
    def last_exception(self):
        return self._last_exception

    def is_error(self):
        return self._error.is_set()

    def is_passsword_grant(self):
        """check is it a password grant"""
        assert isinstance(self._grant, GrantPassword) or isinstance(
            self._grant, GrantRefreshToken
        )
        return isinstance(self._grant, GrantPassword)

    def run(self):
        """run the authentication token handler thread"""
        try:
            self._session.debug(f"STARTING :: {self.name}.run()")
            self._start_event.set()

            #   create new asyncio loop for this thread
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

            #   do first authorize to the RDP server
            self._authorize()
            #   done
            self._ready.set()

            #   run until the stop event is set
            debug_refresh_token_printing_time = time.time()
            while not self._stop_event.is_set():
                assert (
                    self._authentication_token_information is not None
                    and self._token_expires_in_secs is not None
                    and self._token_requested_time is not None
                ), "ERROR!!! Something is wrong in the _request_refresh_token function."

                #   check do we need to request a new token or not?
                #       calculate delay before next request token time
                now = time.time()
                if debug_refresh_token_printing_time < now:
                    delay = (
                        self._token_requested_time + self._token_expires_in_secs - now
                    )
                    self._session.debug(
                        f"    now                   = {now}\n    token_requested_time  = {self._token_requested_time}\n    token_expires_in_secs = {self._token_expires_in_secs}\n    delay                 = {delay}"
                    )
                    debug_refresh_token_printing_time = (
                        now + self._token_expires_in_secs / 6.5
                    )

                if now > self._token_requested_time + (
                    self._token_expires_in_secs // 2
                ):
                    self._request_new_authentication_token_event.set()
                else:
                    #   wait and check for the request new authentication token
                    self._request_new_authentication_token_event.wait(1)

                #   the request new authentication token is set, so request it now
                if self._request_new_authentication_token_event.is_set():
                    self._request_refresh_token()

                    #   reset the event
                    self._request_new_authentication_token_event.clear()
                    self._ready.set()

            self._session.debug(f"STOPPED :: {self.name}.run()")

        except Exception as e:
            #   get an exception from authentication process, so stop
            self._session.error(
                f"ERROR!!! authentication handler raise an exception.\n{e!r}"
            )

            self._error.set()
            #   store the last exception
            self._last_exception = e

        #   cleanup asyncio loop
        self._loop.close()

    def stop(self):
        """stop the authentication token thread"""

        #   check for stop, only if thread started
        if self._start_event.is_set():
            #   stop the authentication thread
            self._stop_event.set()
            #   wait the thread to be finished
            self.join()

        self._session.debug("Authentication token handler thread STOPPED.")

    def wait_for_authorize_ready(self, timeout_secs=None):
        timeout_secs = 5 if timeout_secs is None else timeout_secs
        self._ready.wait(timeout_secs) or self._error.wait(timeout_secs)

    def authorize(self):
        """do an authorize to the RDP services. this function will spawn a new thread if it doesn't exist."""
        self._session.debug(f"{self.name}.authorize()")
        assert (
            not self.is_error()
        ), f"ERROR!!! AuthenticationTokenHandlerThread has an error.\n{self._last_exception}"

        #   clear the ready flag
        self._ready.clear()

        #   check the thread is running or not?
        if not self._start_event.is_set():
            #   thread doesn't start yet, so start it
            assert (
                not self.is_alive()
            ), "ERROR!!! authentication thread has been started."
            #   run the first authorize to RDP authentication endpoint

            #   run thread
            self._session.debug("starting the authentication thread.........")
            self.start()
        else:
            #   thread is already started, so trigger the request new authentication event
            self._session.debug("requesting a new authentication token........")
            self._request_new_authentication_token_event.set()

    def _authorize(self):
        """do an authorize for a token"""

        #   do request a the token
        if isinstance(self._grant, GrantPassword):
            #   request by password
            (response, token_information) = self._request_token_by_password(
                client_id=self._session.app_key,
                username=self._grant.get_username(),
                password=self._grant.get_password(),
                scope=self._grant.get_token_scope(),
                take_exclusive_sign_on_control=True,
            )
        elif isinstance(self._grant, GrantRefreshToken):
            #   request by token
            (response, token_information) = self._request_token_by_refresh_token(
                client_id=self._session.app_key,
                username=self._grant.get_username(),
                refresh_token=self._grant.get_refresh_token(),
            )
        else:
            #   unknown grant type
            error_message = f"ERROR!!! unknown grant type {self._grant}"
            self._session.error(error_message)
            self._session.report_session_status(
                self._session,
                self._session.EventCode.SessionAuthenticationFailed,
                error_message,
            )

            #   raise an error
            raise KeyError("ERROR!!! invalid grant type")

        #   check the response is successfully or not
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            #   got a 4xx or 5xx responses.
            error_message = f"ERROR!!! response {e.response.status_code} while requesting {e.request.url!r}.\n      {response.text}"
            self._session.error(error_message)
            self._session.report_session_status(
                self._session,
                self._session.EventCode.SessionAuthenticationFailed,
                error_message,
            )

            #   raise an error
            raise e

        self._session.report_session_status(
            self._session,
            self._session.EventCode.SessionAuthenticationSuccess,
            "Successfully authorized to RDP authentication endpoint.",
        )

        #   successfully request a token
        self._authentication_token_information = token_information

        #   schedule the next request refresh token
        self._schedule_next_request_refresh_token(token_information)

        #   update the access token in session
        self._update_authentication_access_token(token_information.access_token)

    def _update_authentication_access_token(self, access_token):
        """update authentication token in the session including all the stream connection"""
        self._session.debug(
            f"{self.name}._update_authentication_access_token(access_token={access_token})"
        )

        #   update the session access token (be careful this is another thread from the session)
        self._loop.call_soon_threadsafe(self._session.set_access_token(access_token))
        self._loop.call_soon_threadsafe(
            self._session.set_stream_authentication_token(access_token)
        )

    def _schedule_next_request_refresh_token(self, token_information):
        """schedule the next request for a refresh token"""
        self._session.debug(f"{self.name}._schedule_next_request_refresh_token()")

        #   planing a next request a refresh token

        #   calculate the next request refresh token
        self._token_expires_in_secs = float(token_information.expires_in)
        self._session.debug(
            f"        a refresh token will be expired in {self._token_expires_in_secs} secs"
        )

    def _request_refresh_token(self):
        """request a refresh token"""
        self._session.debug(f"{self.name}._request_refresh_token()")

        #   loop until request for a refresh token is success or fail
        refreshed_token_information = None
        response = None
        while True:
            try:
                #   do request a refresh token
                (
                    response,
                    refreshed_token_information,
                ) = self._request_token_by_refresh_token(
                    client_id=self._session.app_key,
                    username=self._grant.get_username(),
                    refresh_token=self._authentication_token_information.refresh_token,
                )
            except httpx.RequestError as e:
                #   try to request a refresh again
                self._session.error(
                    f"An error occurred while requesting {e.request.url!r}. with : {e}"
                )
                self._session.debug(f"          try to send a refresh token again.")

                #   waiting for few seconds, before request again
                time.sleep(1)
                continue

            except Exception as e:
                #   somthing wrong when request the refresh token
                self._session.error(
                    f"ERROR!!! something wrong while requesting a refresh token.\n   {e}"
                )
                self._session.debug(f"          try to refresh a token again.")

                #   waiting for few seconds, before request again
                time.sleep(1)
                continue

            else:
                #   request successfully
                break

        #   check the response status
        if response is not None and not response.is_error:
            #   successfully request a refresh token
            self._session.info(
                "Successfully refresh an authentication token..........."
            )

        else:
            #   failed

            #   check do it need to retry until the request is successfully
            if self._server_mode and self.is_passsword_grant():
                #   server mode is enable, retry by request token by password if it cannot refresh token.
                self._session.debug(
                    "server mode is enable, retry by request token by password if it cannot refresh token."
                )

                #   try to request the authentication token

                #   loop until the refresh token is successfully or re-authorize by password
                while True:

                    #   waiting for few seconds, before request
                    time.sleep(1)

                    #   do request a refresh token by password
                    assert isinstance(
                        self._grant, GrantPassword
                    ), "it is not a GrantPassword, so we cannot re-authorize with authentication server."
                    try:
                        (
                            response,
                            refreshed_token_information,
                        ) = self._request_token_by_password(
                            client_id=self._session.app_key,
                            username=self._grant.get_username(),
                            password=self._grant.get_password(),
                            scope=self._grant.get_token_scope(),
                            take_exclusive_sign_on_control=self._take_exclusive_sign_on_control,
                        )
                    except httpx.RequestError as e:
                        #   try to request a new token again
                        self._session.error(
                            f"An error occurred while requesting {e.request.url!r} with : {e}"
                        )
                        self._session.debug(f"          try request token again.")

                        #   request again
                        continue

                    except Exception as e:
                        #   somthing wrong when request the refresh token
                        self._session.error(
                            f"ERROR!!! something wrong while requesting a new token by username/password.\n   {e}"
                        )
                        self._session.debug(
                            f"          try request token again with username/password again."
                        )

                        #   waiting for few seconds, before request again
                        time.sleep(1)
                        continue

                    #   check the response status
                    if not response.is_error:
                        #   successfully request a refresh token

                        #   build successful refresh message
                        message = (
                            "Successfully refresh an authentication token..........."
                        )
                        self._session.info(message)
                        self._session.report_session_status(
                            self._session,
                            self._session.EventCode.SessionAuthenticationSuccess,
                            message,
                        )

                        #   done
                        break

                    #   check the 4xx/5xx status code for client/server error
                    if 400 <= response.status_code < 500:
                        #   client error code, don't raise the exception because this is a server-mode,
                        #       it somethings is failed based on client issue, we just keep requesting a new token
                        self._session.error(
                            "ERROR!!! FAILED to refresh an authentication token..........."
                        )

                        #    build the error message and propagate
                        error_message = f"ERROR!!! FAILED refresh an authentication token with response [{response.status_code}] {response.text} while requesting {response.url!r}."
                        self._session.error(error_message)
                        self._session.report_session_status(
                            self._session,
                            self._session.EventCode.SessionAuthenticationFailed,
                            error_message,
                        )

                    else:
                        #   server error code, so retry with password
                        assert (
                            500 <= response.status_code < 600
                        ), "Received the server error after request a new authorization to authentication server."

            else:
                #   server mode is disable, so do need to retry
                #       and failed to request a refresh token

                #    build the error message and propagate
                error_message = f"ERROR!!! request a new refresh token has been failed.\nThe server-mode is disabled, so we do not re-authorize with username/password."
                self._session.error(error_message)
                self._session.report_session_status(
                    self._session,
                    self._session.EventCode.SessionAuthenticationFailed,
                    error_message,
                )
                raise ValueError(error_message)

        assert (
            refreshed_token_information is not None
        ), "ERROR!!! Something is wrong in the above _request_refresh_token function."

        #   done
        self._authentication_token_information = refreshed_token_information

        #   schedule the next request refresh token
        self._schedule_next_request_refresh_token(refreshed_token_information)

        #   update the access token in session
        self._update_authentication_access_token(
            refreshed_token_information.access_token
        )

    def _request_token_by_password(
        self,
        client_id: str,
        username: str,
        password: str,
        scope: str,
        take_exclusive_sign_on_control: bool,
    ):
        """request the new token using username and password

        Raise
        ---------
            httpx.RequestError
                if cannot request the the authentication endpoint

            httpx.HTTPStatusError
                if the response is 4xx or 5xx.
        """

        #   build request header
        request_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        #   build request data
        request_data = {
            "grant_type": "password",
            "client_id": client_id,
            "username": username,
            "password": password,
            "scope": scope,
            "takeExclusiveSignOnControl": take_exclusive_sign_on_control,
        }

        self._session.debug(
            f"Send a token request to {self._authentication_endpoint_url}"
        )
        self._session.debug(
            f"{{ 'grant_type' : 'password',\n'client_id' : {client_id[-4:].rjust(len(client_id), '*')},\n'username' : {username},\n'password' : {'*'.join(['*' for i in range(len(password))])},\n'scope' : {scope},\n'takeExclusiveSignOnControl' : {take_exclusive_sign_on_control} }}"
        )

        #   call http request
        (response, token_information) = self.__request_token(
            request_header, request_data
        )

        #   done
        return (response, token_information)

    def _request_token_by_refresh_token(
        self, client_id: str, username: str, refresh_token: str
    ):
        """request the new token using username and refresh token

        Raise
        ---------
            httpx.RequestError
                if cannot request the the authentication endpoint

            httpx.HTTPStatusError
                if the response is 4xx or 5xx.
        """

        #   build request header
        assert (
            self._authentication_token_information.access_token is not None
        ), "AuthenticationTokenHandlerThread._request_token_by_refresh_token() does not have a refresh token."
        request_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        #   build request data
        request_data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "username": username,
            "refresh_token": refresh_token,
        }

        self._session.debug(
            f"Send a token request to {self._authentication_endpoint_url}"
        )
        self._session.debug(
            f"{{ 'grant_type' : 'refresh_token',\n'client_id' : {client_id[-4:].rjust(len(client_id), '*')},\n'username' : {username},\n'refresh_token' : {refresh_token[-4:].rjust(len(refresh_token), '*')}\n }}"
        )

        #   call http request
        (response, token_information) = self.__request_token(
            request_header, request_data
        )

        #   done
        return (response, token_information)

    def __request_token(self, request_header, request_data):
        """request the token to authentication endpoint

        Raise
        ---------
            httpx.RequestError
                if cannot request the the authentication endpoint

            httpx.HTTPStatusError
                if the response is 4xx or 5xx.
        """

        #   store the request token timestamp
        self._token_requested_time = time.time()

        #   build a request
        http_request_obj = httpx.Request(
            method="POST",
            url=self._authentication_endpoint_url,
            headers=request_header,
            data=request_data,
        )

        #   do request async to http server
        with httpx.Client() as client:
            response = client.send(
                http_request_obj, timeout=self._session.http_request_timeout_secs
            )

        assert (
            response is not None
        ), "AuthenticationTokenHandlerThread.__request_token() got a None response."
        self._session.debug(f"HTTP response {response.status_code}: {response.text}")

        #   extract header and check the content type
        headers = response.headers
        if "Content-Type" in headers and "/json" in headers.get("Content-Type"):
            #   parse the response
            (response, token_information) = self._parse_request_token_response(response)
        else:
            #   invalid response type
            error_message = f"ERROR!!! Invalid response content type only accept /json.\n      response = {response.content}."
            self._session.error(error_message)
            self._session.report_session_status(
                self._session,
                self._session.EventCode.SessionAuthenticationFailed,
                error_message,
            )
            raise ValueError(error_message)

        #   successfully request token
        return (response, token_information)

    def _parse_request_token_response(self, response):
        """parse the response data from the token request

        response example:

        Ok
            {
                "access_token": "string",
                "expires_in": "string",
                "refresh_token": "string",
                "scope": "string",
                "token_type": "string"
            }

        Error

            {
                "error": "string",
                "error_description": "string",
                "error_uri": "string"
            }

        """

        #   check the response successfully or not?
        if not response.is_error:
            #   successfully request a new token
            #   extract the response
            response_data = response.json()

            self._session.debug("Successfully request a new token......")
            self._session.debug(f"           Token requested response {response_data}")

            assert (
                "access_token" in response_data
            ), 'AuthenticationTokenHandlerThread._parse_request_token_response() "access_token" not in response'
            assert (
                "expires_in" in response_data
            ), 'AuthenticationTokenHandlerThread._parse_request_token_response() "expires_in" not in response'
            assert (
                "scope" in response_data
            ), 'AuthenticationTokenHandlerThread._parse_request_token_response() "scope" not in response'
            assert (
                "token_type" in response_data
            ), 'AuthenticationTokenHandlerThread._parse_request_token_response() "token_type" not in response'

            #   build the token information
            return (
                response,
                self.AuthenticationTokenInformation(
                    access_token=response_data["access_token"],
                    expires_in=response_data["expires_in"],
                    refresh_token=response_data.get("refresh_token", None),
                    scope=response_data["scope"],
                    token_type=response_data["token_type"],
                ),
            )

        else:
            #   failed to request a new token
            self._session.error("ERROR!!! Failed to request a new token......")
            self._session.error(f"         Token requested error {response.content}")
            return (response, None)
