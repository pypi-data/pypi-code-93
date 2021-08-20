# coding: utf-8

__all__ = ["PlatformSession"]

import urllib.parse

from refinitiv.dataplatform import configure
from refinitiv.dataplatform.errors import PlatformSessionError
from refinitiv.dataplatform.tools._common import urljoin, make_counter, cached_property

from .grant import Grant
from .grant_password import GrantPassword
from .grant_refresh import GrantRefreshToken

from .session import Session

from .connection import (
    DeployedConnection,
    RefinitivDataAndDeployedConnection,
    RefinitivDataConnection,
)


class PlatformSession(Session):
    """This class is designed for handling the session to Refinitiv Data Platform (RDP) or Deployed Platform (TREP)
    - Refinitiv Data Platform are including handling an authentication and a token management (including refreshing token),
        also handling a real-time service discovery to get the service websocket endpoint
        and initialize the login for streaming
    - Deployed Platform is including the login for streaming
    """

    __inst_count = make_counter()

    class Params(Session.Params):
        def __init__(self, *args, **kwargs):
            super(PlatformSession.Params, self).__init__(*args, **kwargs)

            self._grant = kwargs.get("grant")
            _signon_control = kwargs.get("signon_control", "False")
            self._take_signon_control = _signon_control.lower() == "true"

            if self._take_signon_control is None:
                self._take_signon_control = False

            #   for deployed platform connection
            self._deployed_platform_host = kwargs.get("deployed_platform_host")

        def get_grant(self):
            return self._grant

        def grant_type(self, grant):
            if isinstance(grant, Grant):
                self._grant = grant
            else:
                raise Exception("wrong Elektron authentication parameter")
            return self

        def take_signon_control(self):
            return self._take_signon_control

        def with_take_signon_control(self, value):
            if value is not None:
                self._take_signon_control = value
            return self

        #   for deployed platform connection
        def deployed_platform_host(self, deployed_platform_host):
            self._deployed_platform_host = deployed_platform_host
            return self

        def with_authentication_token(self, token):
            if token:
                self._dacs_params.authentication_token = token
            return self

    def get_session_params(self):
        return self._session_params

    def session_params(self, session_params):
        self._session_params = session_params
        return session_params

    def _get_rdp_url_root(self):
        return configure.get_str(configure.keys.platform_base_uri(self._session_name))

    @cached_property
    def name(self):
        return f"session.platform.{PlatformSession.__inst_count()}"

    def __init__(
        self,
        app_key=None,
        # for Refinitiv Dataplatform connection
        grant=None,
        signon_control=None,
        # for Deployed platform connection
        deployed_platform_host=None,
        deployed_platform_connection_name=None,
        authentication_token=None,
        deployed_platform_username=None,
        dacs_position=None,
        dacs_application_id=None,
        on_state=None,
        on_event=None,
        # other
        **kwargs,
    ):
        super().__init__(
            app_key,
            on_state=on_state,
            on_event=on_event,
            deployed_platform_username=deployed_platform_username,
            dacs_position=dacs_position,
            dacs_application_id=dacs_application_id,
            **kwargs,
        )

        #   for Refinitiv Dataplatform connection
        self._ws_endpoints = []

        if grant and isinstance(grant, GrantPassword):
            self._grant = grant

        self._take_signon_control = signon_control if signon_control else True

        self._pending_stream_queue = []
        self._pending_data_queue = []

        self._access_token = None
        self._token_expires_in_secs = 0
        self._token_expires_at = 0

        self._websocket_endpoint = None

        # for Deployed platform connection
        #       the host contains host name and port i.e. 127.0.0.0:15000
        self._deployed_platform_host = deployed_platform_host
        self._deployed_platform_connection_name = self._session_name

        #   initialize the realtime distribution system from config file
        self._initialize_realtime_distribution_system_config()

        # classify the connection type
        if grant is not None and self._deployed_platform_host:
            # both connection to Refinitiv Data Platform (RDP) and Deployed Platform
            self.debug(
                "connecting to Refinitiv Data Platform (RDP) and Deployed Platform......."
            )
            self._connection = RefinitivDataAndDeployedConnection(self)
        elif grant is not None:
            # only RDP connection
            self.debug("connecting to Refinitiv Data Platform (RDP) only.......")
            self._connection = RefinitivDataConnection(self)
        elif self._deployed_platform_host:
            # only deployed platform connection
            self.debug("connecting to realtime distribution system only.......")
            self._connection = DeployedConnection(self)
            # self._streaming_connection_name_to_status[self._deployed_platform_connection_name] = Session.EventCode.StreamDisconnected
        else:
            raise AttributeError(
                f"Error!!! Can't initialize a PlatformSession "
                f"without Refinitiv Data Platform Grant (grant user and password) and Deployed Platform host"
            )

    ############################################################
    #   reconnection configuration

    @property
    def stream_auto_reconnection(self):
        session_name = (
            self._session_name
            if self._session_name in configure.config
            else "default-session"
        )
        return configure.config.get_bool(
            configure.keys.platform_auto_reconnect(session_name)
        )

    @property
    def server_mode(self):
        session_name = (
            self._session_name
            if self._session_name in configure.config
            else "default-session"
        )
        return configure.config.get_bool(
            configure.keys.platform_server_mode(session_name)
        )

    ############################################################
    #   session configuration

    @property
    def authentication_token_endpoint_url(self):
        #   authentication url
        authentication_path = configure.config.get_str(
            configure.keys.platform_auth_uri(self._session_name)
        )
        #   token path
        token_path = configure.config.get_str(
            configure.keys.platform_token_uri(self._session_name)
        )

        #   build authentication token url
        authentication_token_endpoint_url = urljoin(
            urljoin(self._get_rdp_url_root(), authentication_path), token_path
        )
        self.debug(
            f"authentication_token_endpoint_url : {authentication_token_endpoint_url}"
        )

        #   done
        return authentication_token_endpoint_url

    def _get_auth_token_uri(self):
        base_auth_uri = configure.config.get_str(
            configure.keys.platform_auth_uri(self._session_name)
        )
        token_uri = configure.config.get_str(
            configure.keys.platform_token_uri(self._session_name)
        )
        auth_token_uri = urljoin(base_auth_uri, token_uri)
        uri = urljoin(self._get_rdp_url_root(), auth_token_uri)
        return uri

    def _initialize_realtime_distribution_system_config(self):
        """ check for an initialize the realtime distribution system from config file if the user specific the deployed platform host """

        #   check the user override the deployed platform (aka TREP) or not?
        if self._deployed_platform_host is None:
            #   user doesn't specific the deployed_platform_host, so check realtime distribution system in config file as the deployed platform hostname

            #   build the config path name for the refinitiv realtime host name
            platform_realtime_distribution_system_url_key = f"{configure.keys.platform_realtime_distribution_system(self._session_name)}.url"
            try:
                platform_realtime_distribution_system_url = configure.get_str(
                    platform_realtime_distribution_system_url_key
                )
            except KeyError:
                #   the realtime distribution system doesn't specify in the config file
                #       so, do nothing
                self.debug(
                    f"WARNING!!! the Refinitiv realtime distribution system doesn't specify."
                )
                return

            self.debug(
                f"using the Refinitiv realtime distribution system : url at {platform_realtime_distribution_system_url}"
            )

            #   construct host for host name and port
            self._deployed_platform_host = urllib.parse.urlparse(
                platform_realtime_distribution_system_url
            ).netloc
            self.debug(f"      deployed_platform_host = {self._deployed_platform_host}")

        else:
            #   using the deployed platform host from user specific
            self.debug(
                f"using the specific deployed platform host : host {self._deployed_platform_host}"
            )

    ############################################################
    #   authentication token

    def request_stream_authentication_token(self):
        """ Request new stream authentication token """
        self.debug(f"{self.__class__.__name__}.request_stream_authentication_token()")
        self._connection.authorize()

    ############################################################
    #   multi-websockets support

    def _get_stream_status(self, streaming_connection_name: str):
        """this method is designed for getting a status of given streaming connection.

        Parameters
        ----------
            a connection string of stream
        Returns
        -------
        enum
            status of stream service.
        """
        return self._connection.get_stream_status(streaming_connection_name)

    def _set_stream_status(self, streaming_connection_name: str, stream_status):
        """set status of given streaming connection

        Parameters
        ----------
        string
            a connection string of stream
        enum
            a status enum of stream
        Returns
        -------
        """
        self._connection.set_stream_status(streaming_connection_name, stream_status)

    async def _get_stream_connection_configuration(self, stream_connection_name: str):
        """
        This method is designed to retrieve the stream connection configuration.

        Parameters
        ----------
        stream_connection_name
            a name of stream connection in the config file i.e. "streaming/pricing/main"

        Returns
        -------
        obj
            a stream connection configuration object

        Raises
        -------
        EnvError
            if the given stream_connection_name is invalid.
        """
        return await self._connection.get_stream_connection_configuration(
            stream_connection_name
        )

    #################################################
    #   OMM and RDP login message for each kind of session ie. desktop, platform or deployed platform

    def get_omm_login_message_key_data(self):
        """Return the login message for OMM 'key' section"""
        return self._connection.get_omm_login_message_key_data()

    def get_rdp_login_message(self, stream_id):
        """return the login message for RDP"""
        return {
            "streamID": f"{stream_id:d}",
            "method": "Auth",
            "token": self._access_token,
        }

    #######################################
    #  methods to open and close session  #
    #######################################

    def close(self):
        """ Close all connection from both Refinitiv Data Platform and Deployed Platform (TREP) """
        self._connection.close()

        #   call parent for class
        Session.close(self)

    ############################################
    #  methods to open asynchronously session  #
    ############################################
    async def open_async(self):
        def open_state():
            self._state = Session.State.Open
            self._on_state(self._state, "Session is opened.")

        if self._state in [Session.State.Pending, Session.State.Open]:
            # session is already opened or is opening
            return self._state

        #   do authentication process with Refinitiv Data Platform (RDP), if it's necessary
        self._connection.open()

        #   the platform session is ready,
        open_state()

        #   call parent call open_async
        await super(PlatformSession, self).open_async()

        #   waiting for everything ready
        await self._connection.waiting_for_stream_ready(open_state)

        #   done, return state
        return self._state

    ############################
    # methods for HTTP request #
    ############################
    async def http_request_async(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        return await self._connection.http_request_async(
            url,
            method=method,
            headers=headers,
            data=data,
            params=params,
            json=json,
            closure=closure,
            auth=auth,
            loop=loop,
            **kwargs,
        )
