from __future__ import annotations

from enum import Enum, auto
from typing import Optional


class ConfigQueueType(Enum):
    REQUEST = auto()

    @staticmethod
    def to_enum(value: str) -> Optional[ConfigQueueType]:
        v: str = value.upper().replace(" ", "-").replace("-", "_")
        return ConfigQueueType[v]

    def value(self) -> str:
        return self.name.lower()
