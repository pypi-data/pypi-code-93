from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from ctlml_commons.entity.execution_type import ExecutionType
from ctlml_commons.entity.order import OrderType
from ctlml_commons.entity.time_in_force import TimeInForce
from ctlml_commons.util.date_utils import convert_dates
from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class ExecutionDecision:
    """Provides fine level granularity of an execution decision."""

    symbol: str
    execution_type: ExecutionType
    price: float
    quantity: float
    time: datetime
    notes: str
    order_type: Optional[OrderType] = None
    time_in_force: Optional[TimeInForce] = None

    def serialize(self) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(self.__dict__)

        data["execution_type"] = self.execution_type.value()
        data["time"] = str(self.time)

        if self.order_type:
            data["order_type"] = self.order_type.value()
        if self.time_in_force:
            data["time_in_force"] = self.time_in_force.value()

        return data

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> ExecutionDecision:
        return cls(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["execution_type"] = ExecutionType.to_enum(data["execution_type"])
        data = convert_floats(data, ["quantity", "price"])
        data = convert_dates(data, "time")

        if "order_type" in data:
            data["order_type"] = OrderType.to_enum(data["order_type"])
        if "time_in_force" in data:
            data["time_in_force"] = TimeInForce.to_enum(data["time_in_force"])

        return data
