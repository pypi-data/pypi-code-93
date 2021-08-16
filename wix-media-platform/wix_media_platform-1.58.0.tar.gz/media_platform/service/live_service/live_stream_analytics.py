from __future__ import annotations

from typing import List, Dict

from media_platform.lang.serialization import Serializable, Deserializable


class LiveStreamAnalytics(Serializable, Deserializable):
    def __init__(self, project_id: str, stream_id: str = None, stats: List[Dict] = None):
        self.project_id = project_id
        self.stream_id = stream_id
        self.stats = stats or []

    @classmethod
    def deserialize(cls, data: Dict) -> LiveStreamAnalytics:
        return cls(data['projectId'], data['streamId'], data['stats'])

    def serialize(self) -> Dict:
        return {
            'streamId': self.stream_id,
            'projectId': self.project_id,
            'stats': self.stats
        }
