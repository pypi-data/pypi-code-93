from __future__ import annotations

from media_platform.service.live_service.close_stream_request import CloseStreamRequest
from media_platform.service.live_service.get_stream_analytics_request import GetStreamAnalyticsRequest
from media_platform.service.live_service.get_stream_frame_request import GetStreamFrameRequest
from media_platform.service.live_service.get_stream_request import GetStreamRequest
from media_platform.service.live_service.list_streams_request import ListStreamsRequest
from media_platform.service.live_service.open_stream_request import OpenStreamRequest
from media_platform.service.media_platform_service import MediaPlatformService


class LiveService(MediaPlatformService):
    def open_stream_request(self) -> OpenStreamRequest:
        return OpenStreamRequest(self._authenticated_http_client, self._base_url)

    def close_stream_request(self, *args, **kwargs) -> CloseStreamRequest:
        return CloseStreamRequest(self._authenticated_http_client, self._base_url, *args, **kwargs)

    def get_stream_request(self) -> GetStreamRequest:
        return GetStreamRequest(self._authenticated_http_client, self._base_url)

    def get_stream_frame_request(self, *args, **kwargs) -> GetStreamFrameRequest:
        return GetStreamFrameRequest(self._authenticated_http_client, self._base_url, *args, **kwargs)

    def get_stream_analytics_request(self, *args, **kwargs) -> GetStreamAnalyticsRequest:
        return GetStreamAnalyticsRequest(self._authenticated_http_client, self._base_url, *args, **kwargs)

    def list_streams_request(self, *args, **kwargs) -> ListStreamsRequest:
        return ListStreamsRequest(self._authenticated_http_client, self._base_url, *args, **kwargs)
