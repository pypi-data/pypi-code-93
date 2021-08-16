from __future__ import annotations

from typing import Optional, Dict, cast

from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.live_service.enforced_stream_params import EnforcedStreamParams
from media_platform.service.live_service.geo_location import GeoLocation
from media_platform.service.live_service.live_stream import LiveStream
from media_platform.service.live_service.stream_dvr import StreamDVR
from media_platform.service.live_service.stream_protocol import StreamProtocol
from media_platform.service.live_service.stream_state_notification import StreamStateNotification
from media_platform.service.live_service.stream_type import StreamType
from media_platform.service.media_platform_request import MediaPlatformRequest


class OpenStreamRequest(MediaPlatformRequest):
    def __init__(self, authenticated_http_client: AuthenticatedHTTPClient, base_url: str):
        super().__init__(authenticated_http_client, 'POST', base_url + '/live/streams', LiveStream)
        self.protocol: Optional[StreamProtocol] = None
        self.dvr: Optional[StreamDVR] = None
        self.geo: Optional[GeoLocation] = None
        self.max_stream_time_sec: Optional[int] = None
        self.state_notification: Optional[StreamStateNotification] = None
        self.stream_type: StreamType = StreamType.event
        self.connect_timeout: Optional[int] = None
        self.reconnect_timeout: Optional[int] = None
        self.enforced_stream_params: Optional[EnforcedStreamParams] = None
        self.version: Optional[str] = None

    def set_protocol(self, protocol: StreamProtocol) -> OpenStreamRequest:
        self.protocol = protocol
        return self

    def set_dvr(self, dvr: StreamDVR) -> OpenStreamRequest:
        self.dvr = dvr
        return self

    def set_geo(self, geo: GeoLocation) -> OpenStreamRequest:
        self.geo = geo
        return self

    def set_max_stream_time_sec(self, max_stream_time_sec) -> OpenStreamRequest:
        self.max_stream_time_sec = max_stream_time_sec
        return self

    def set_state_notification(self, state_notification: StreamStateNotification) -> OpenStreamRequest:
        self.state_notification = state_notification
        return self

    def set_stream_type(self, stream_type: StreamType) -> OpenStreamRequest:
        self.stream_type = stream_type
        return self

    def set_connect_timeout(self, connect_timeout: int) -> OpenStreamRequest:
        self.connect_timeout = connect_timeout
        return self

    def set_reconnect_timeout(self, reconnect_timeout: int) -> OpenStreamRequest:
        self.reconnect_timeout = reconnect_timeout
        return self

    def set_enforced_stream_params(self, enforced_stream_params: EnforcedStreamParams) -> OpenStreamRequest:
        self.enforced_stream_params = enforced_stream_params
        return self

    def set_version(self, host_key: str) -> OpenStreamRequest:
        self.version = host_key
        return self

    def execute(self) -> LiveStream:
        if self.version:
            self.url += '?version=' + self.version

        return cast(LiveStream, super().execute())

    def _params(self) -> Dict:
        return {
            'protocol': self.protocol,
            'maxStreamingSec': self.max_stream_time_sec,
            'streamType': self.stream_type,
            'connectTimeout': self.connect_timeout,
            'reconnectTimeout': self.reconnect_timeout,
            'enforcedStreamParams': self.enforced_stream_params.serialize() if self.enforced_stream_params else None,
            'stateNotification': self.state_notification.serialize() if self.state_notification else None,
            'dvr': self.dvr.serialize() if self.dvr else None,
            'geo': self.geo.serialize() if self.geo else None
        }
