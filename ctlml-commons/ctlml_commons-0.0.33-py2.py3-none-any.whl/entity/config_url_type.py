from __future__ import annotations

from enum import Enum, auto
from typing import Optional


class ConfigUrlType(Enum):
    ACCOUNTS = auto()
    CANDLES = auto()
    COINBASE = auto()
    DOW = auto()
    EXECUTOR = auto()
    MANAGER = auto()
    ROBINHOOD = auto()
    RUSSELL = auto()
    SANDP = auto()
    STATS = auto()
    STOCKS = auto()
    TICKERS = auto()
    TRANSACT = auto()
    USERS = auto()
    USER_STOCKS = auto()

    @staticmethod
    def to_enum(value: str) -> Optional[ConfigUrlType]:
        v: str = value.upper().replace(" ", "-").replace("-", "_")
        return ConfigUrlType[v]

    def value(self) -> str:
        return self.name.lower()
