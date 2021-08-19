from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict

from ctlml_commons.entity.time_in_force import TimeInForce


@dataclass(frozen=True)
class LimitBuySellRequest:
    symbol: str
    quantity: float
    price: float
    time_in_force: TimeInForce
    extended_hours: bool = False
    testing: bool = False

    def serialize(self) -> Dict[str, Any]:
        data = deepcopy(self.__dict__)

        data["time_in_force"] = TimeInForce.from_enum(self.time_in_force)

        return data

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> LimitBuySellRequest:
        return LimitBuySellRequest(**LimitBuySellRequest.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["time_in_force"] = TimeInForce.to_enum(data["time_in_force"])

        return data
