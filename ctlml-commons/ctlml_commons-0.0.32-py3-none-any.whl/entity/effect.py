from __future__ import annotations

from enum import Enum, auto


class Effect(Enum):
    OPEN = auto()
    CLOSE = auto()

    @staticmethod
    def to_enum(value: str) -> Effect:
        v: str = value.upper()
        return Effect[v]

    def value(self) -> str:
        return self.name.lower()
