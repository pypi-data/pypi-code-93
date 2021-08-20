# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

import abc

###############################################################
#
#   REFINITIV IMPORTS
#

from refinitiv.dataplatform.core.session.proxy_info import ProxyInfo

###############################################################
#
#   LOCAL IMPORTS
#


###############################################################
#
#   CLASS DEFINITIONS
#


class StreamConnectionConfiguration(abc.ABC):
    """this class is designed for storing the stream connection configuration.
    i.e. desktop data api proxy, service discovery, realtime-distribution-system, etc.
    """

    #   default delay time before do a reconnection in secs
    _DefaultReconnectionDelayTime_secs = 5

    def __init__(
        self,
        session: object,
        stream_service_information_list: list,
        supported_protocol_list: list,
    ):
        assert session is not None
        self._session = session

        assert (
            stream_service_information_list is not None
            and len(stream_service_information_list) > 0
        )
        self._stream_service_information_list = stream_service_information_list

        assert supported_protocol_list is not None and len(supported_protocol_list) > 0
        self._supported_protocol_list = supported_protocol_list

        # 	store the current index of stream service
        self._current_stream_service_information_index = 0

    @property
    def stream_service_information(self):
        assert self._current_stream_service_information_index < len(
            self._stream_service_information_list
        )
        return self._stream_service_information_list[
            self._current_stream_service_information_index
        ]

    @property
    def url(self):
        return self._build_stream_connection_url(self.stream_service_information)

    @property
    def url_scheme(self):
        return self.stream_service_information.scheme

    @property
    def urls(self):
        return [
            self._build_stream_connection_url(stream_service_information)
            for stream_service_information in self._stream_service_information_list
        ]

    @property
    def headers(self):
        return []

    @property
    def data_formats(self):
        return self.stream_service_information.data_formats

    @property
    def supported_protocols(self):
        return self._supported_protocol_list

    @property
    def reconnection_delay_secs(self):
        return (
            self._current_stream_service_information_index
            * self._DefaultReconnectionDelayTime_secs
        )

    def set_next_available_websocket_url(self):
        self._current_stream_service_information_index = (
            self._current_stream_service_information_index + 1
            if self._current_stream_service_information_index + 1
            < len(self._stream_service_information_list)
            else 0
        )

    def reset_reconnection_config(self):
        self._current_stream_service_information_index = 0

    #############################
    # 	proxy section

    @property
    def no_proxy(self):
        return ProxyInfo.get_no_proxy()

    @property
    def proxy_config(self):
        proxies_info = ProxyInfo.get_proxies_info()
        if self.url_scheme == "wss":
            # try to get https proxy then http proxy if https not configured
            return proxies_info.get("https", proxies_info.get("http", None))
        else:
            return proxies_info.get("http", None)

    ###########################################################################################
    # warning REMOVE_ME :: AFTER UPGRADE THE PLATFORM TO USE DISCOVERY ENDPOINT
    @property
    def uri(self):
        return self.url

    @property
    def uris(self):
        return self.urls

    @property
    def data_fmt(self):
        return self.data_format[0]

    @property
    def delay(self):
        return self.reconnection_delay_secs

    def set_next_url(self):
        self.set_next_available_websocket_url()

    def set_next_delay(self, val=None):
        self.reset_reconnection_config()

    ###########################################################################################

    ################################################################
    # 	internal functions

    @abc.abstractmethod
    def _build_stream_connection_url(self, stream_service_information):
        """ implement this function for specific type of servicer discovery or difference version of it """
        pass


class DesktopStreamConnectionConfiguration(StreamConnectionConfiguration):
    """ this class is designed for handling the desktop session stream connection configuration """

    def __init__(
        self,
        session: object,
        stream_service_information_list: list,
        supported_protocol_list: list,
    ):
        StreamConnectionConfiguration.__init__(
            self, session, stream_service_information_list, supported_protocol_list
        )

    @property
    def headers(self):
        return [f"x-tr-applicationid: {self._session.app_key}"]

    def _build_stream_connection_url(self, stream_service_information):
        return f"{stream_service_information.scheme}://{stream_service_information.host}:{stream_service_information.port}/{stream_service_information.path}"


class RealtimeDistributionSystemConnectionConfiguration(StreamConnectionConfiguration):
    """ this class is designed for handling the realtime distribution system (aka. deployed platform host or TREP) """

    def __init__(
        self,
        session: object,
        stream_service_information_list: list,
        supported_protocol_list: list,
    ):
        StreamConnectionConfiguration.__init__(
            self, session, stream_service_information_list, supported_protocol_list
        )

    def _build_stream_connection_url(self, stream_service_information):
        path = (
            "WebSocket"
            if stream_service_information.path is None
            or stream_service_information.path == ""
            else f"{stream_service_information.path}"
        )
        return f"{stream_service_information.scheme}://{stream_service_information.host}:{stream_service_information.port}/{path}"
