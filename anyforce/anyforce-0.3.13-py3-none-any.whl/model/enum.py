from __future__ import annotations

from enum import Enum as Base
from typing import Any, Type


class EnumMissingError(Exception):
    def __init__(
        self, enum_type: Type[Enum], value: Any, *args: object
    ) -> None:
        super().__init__(*args)
        self.enum_type = enum_type
        self.value = value


class Enum(Base):
    @classmethod
    def _missing_(cls, value: Any):
        raise EnumMissingError(cls, value, f"枚举值 {value} 不存在")
