from __future__ import annotations

from enum import Enum, auto


class StatType(Enum):
    BOUGHT = auto()
    SOLD = auto()
    ERRORS = auto()
    PROFIT_LOSS = auto()
    UNREALIZED_PROFIT_LOSS = auto()

    @staticmethod
    def to_enum(value: str) -> StatType:
        v: str = value.upper().replace(" ", "-").replace("-", "_")
        return StatType[v]

    def value(self) -> str:
        return self.name.lower()

    def __str__(self) -> str:
        return self.value()

    def __repr__(self) -> str:
        return self.value()
