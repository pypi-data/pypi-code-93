from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from functools import wraps
from typing import Any, Dict


@dataclass
class Candle2:
    # __slots__ = ["current", "open", "close", "high", "low", "day_high", "day_low", "day_open"]

    current: float = 0.0
    open: float = 0.0
    close: float = 0.0
    high: float = 0.0
    low: float = 0.0
    day_high: float = 0.0
    day_low: float = 0.0
    day_open: float = 0.0

    def serialize(self) -> Dict[str, Any]:
        return deepcopy(self.__dict__)

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Candle:
        return Candle(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return input_data


# def change_init_signature(init):
#     @wraps(init)
#     def __init__(
#             self,
#             current: float = 0.0,
#             open: float = 0.0,
#             close: float = 0.0,
#             high: float = 0.0,
#             low: float = 0.0,
#             day_high: float = 0.0,
#             day_low: float = 0.0,
#             day_open: float = 0.0,
#     ) -> None:
#         init(self, current, open, close, high, low, day_high, day_low, day_open)
#
#     return __init__
#
#
# Candle.__init__ = change_init_signature(Candle.__init__)
# Candle.__dataclass_fields__["current"].default = 0.0
# Candle.__dataclass_fields__["open"].default = 0.0
# Candle.__dataclass_fields__["close"].default = 0.0
# Candle.__dataclass_fields__["high"].default = 0.0
# Candle.__dataclass_fields__["low"].default = 0.0
# Candle.__dataclass_fields__["day_high"].default = 0.0
# Candle.__dataclass_fields__["day_low"].default = 0.0
# Candle.__dataclass_fields__["day_open"].default = 0.0
