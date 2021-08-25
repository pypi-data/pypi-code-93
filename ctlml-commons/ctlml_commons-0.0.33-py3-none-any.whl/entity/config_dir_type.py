from __future__ import annotations

from enum import Enum, auto
from typing import Optional


class ConfigDirType(Enum):
    BASE = auto()
    LOG = auto()
    OUTPUT = auto()
    TMP = auto()

    @staticmethod
    def to_enum(value: str) -> Optional[ConfigDirType]:
        v: str = value.upper().replace(" ", "-").replace("-", "_")
        return ConfigDirType[v]

    def value(self) -> str:
        return self.name.lower()
