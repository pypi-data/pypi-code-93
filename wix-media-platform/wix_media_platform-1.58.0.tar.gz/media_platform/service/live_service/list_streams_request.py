from __future__ import annotations

from typing import Union, List, Dict

from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.live_service.list_streams_response import ListStreamsResponse
from media_platform.service.live_service.stream_list_order import LiveStreamListOrder
from media_platform.service.live_service.stream_list_order_direction import LiveStreamListOrderDirection
from media_platform.service.live_service.stream_state import StreamState
from media_platform.service.media_platform_request import MediaPlatformRequest


class ListStreamsRequest(MediaPlatformRequest):
    def __init__(self, authenticated_http_client: AuthenticatedHTTPClient, base_url: str,
                 state: Union[str, StreamState, List[StreamState]] = None,
                 page_size: int = None,
                 order_by: LiveStreamListOrder = None,
                 order_direction: LiveStreamListOrderDirection = None,
                 next_page_token: str = None,
                 version: str = None):
        super().__init__(authenticated_http_client, 'GET', base_url + '/live/streams', ListStreamsResponse)
        self.page_size = int(page_size) if page_size else None
        self.order_by = order_by
        self.order_direction = order_direction
        self.state = state
        self.next_page_token = next_page_token
        self.version = version

    def _params(self) -> Dict:
        return {
            'state': ','.join(self.state) if isinstance(self.state, list) else self.state,
            'pageSize': self.page_size,
            'orderBy': self.order_by,
            'orderDirection': self.order_direction,
            'nextPageToken': self.next_page_token,
            'version': self.version
        }
