from __future__ import annotations

from enum import Enum, auto


class CashType(Enum):
    CREDIT = auto()
    DEBIT = auto()

    @staticmethod
    def to_enum(value: str) -> CashType:
        v: str = value.upper()
        return CashType[v]

    def value(self) -> str:
        return self.name.lower()
