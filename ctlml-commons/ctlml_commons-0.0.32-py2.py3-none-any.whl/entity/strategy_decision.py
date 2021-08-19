from dataclasses import dataclass

from ctlml_commons.entity.execution_type import ExecutionType


@dataclass(frozen=True)
class StrategyDecision:
    execution_type: ExecutionType
    symbol: str
    shares: float
    price: float
    notes: str
