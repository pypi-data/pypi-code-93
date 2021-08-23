from __future__ import annotations

from typing import Optional, List, Dict

from media_platform.lang.serialization import Serializable, Deserializable
from media_platform.service.live_service.live_stream import LiveStream


class ListStreamsResponse(Serializable, Deserializable):
    def __init__(self, next_page_token: Optional[str], streams: List[LiveStream]):
        self.next_page_token = next_page_token
        self.streams = streams

    def serialize(self) -> Dict:
        return {
            'nextPageToken': self.next_page_token,
            'streams': [stream.serialize() for stream in self.streams if stream]
        }

    @classmethod
    def deserialize(cls, data: Dict) -> ListStreamsResponse:
        return ListStreamsResponse(
            data.get('nextPageToken'),
            [LiveStream.deserialize(d) for d in data['streams']]
        )
