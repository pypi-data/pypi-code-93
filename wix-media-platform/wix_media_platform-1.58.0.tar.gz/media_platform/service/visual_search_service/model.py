from __future__ import annotations
from typing import Dict

from media_platform.lang.serialization import Deserializable


class Model(Deserializable):
    def __init__(self, model_id: str, name: str, description: str):
        self.model_id = model_id
        self.name = name
        self.description = description

    @classmethod
    def deserialize(cls, data: Dict) -> Model:
        return Model(data['id'], data['name'], data['description'])
