from __future__ import annotations
from typing import Dict

from media_platform.lang.serialization import Deserializable


class Collection(Deserializable):
    def __init__(self, collection_id: str, name: str, project_id: str, model_id: str):
        self.collection_id = collection_id
        self.name = name
        self.project_id = project_id
        self.model_id = model_id

    @classmethod
    def deserialize(cls, data: Dict) -> Collection:
        return Collection(data['id'], data['name'], data['projectId'], data['modelId'])
