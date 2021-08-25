from __future__ import annotations

from enum import Enum, auto
from typing import List, Optional


class ExecutionType(Enum):
    EOD = auto()
    SELL = auto()
    BUY = auto()
    WAIT = auto()

    @staticmethod
    def to_enum(value: str) -> Optional[ExecutionType]:
        v: str = value.upper().replace(" ", "-").replace("-", "_")
        return ExecutionType[v]

    @staticmethod
    def by_priority() -> List[ExecutionType]:
        return [ExecutionType.EOD, ExecutionType.SELL, ExecutionType.BUY]

    def value(self) -> str:
        return self.name.lower()

    @staticmethod
    def to_method_name(execution_type: ExecutionType) -> str:
        return {
            ExecutionType.EOD: "sell",
            ExecutionType.SELL: "sell",
            ExecutionType.BUY: "buy",
            ExecutionType.WAIT: "noop",
        }[execution_type]
