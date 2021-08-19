from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, Set


@dataclass(frozen=True)
class Investor:
    name: str
    available_funds: float = 0
    starting_funds: float = 0
    cash_percentage: float = 0
    realized_profit_loss: float = 0.00
    num_transactions: int = 0
    symbols_held: Set[str] = field(default_factory=set)
    default_stocks: Set[str] = field(default_factory=set)
    tracking_stocks: Set[str] = field(default_factory=set)

    def serialize(self) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(self.__dict__)

        for a_set in ["symbols_held", "default_stocks", "tracking_stocks"]:
            data[a_set] = list(data[a_set])

        return data

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Investor:
        return Investor(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        for a_list in ["symbols_held", "default_stocks", "tracking_stocks"]:
            data[a_list] = set(data[a_list])

        return data
