from __future__ import annotations

from enum import Enum, auto


class OptionType(Enum):
    CALL = auto()
    PUT = auto()

    @staticmethod
    def to_enum(value: str) -> OptionType:
        v: str = value.upper().replace(" ", "-").replace("-", "_")
        return OptionType[v]

    def value(self) -> str:
        return self.name.lower()
