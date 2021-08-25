from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from ctlml_commons.entity.execution_type import ExecutionType
from ctlml_commons.entity.order import OrderType
from ctlml_commons.entity.time_in_force import TimeInForce
from ctlml_commons.util.date_utils import convert_dates
from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class ExecutionRequest:
    investor_name: str
    lot_id: UUID
    symbol: str
    execution_type: ExecutionType
    order_type: OrderType
    quantity: float
    time_in_force: TimeInForce
    notes: str
    price: float
    time: datetime

    def serialize(self) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(self.__dict__)

        data["execution_type"] = self.execution_type.value()
        data["order_type"] = self.order_type.value()
        data['time_in_force'] = self.time_in_force.value()
        data["lot_id"] = str(data["lot_id"])
        data["time"] = str(self.time)

        return data

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> ExecutionRequest:
        return ExecutionRequest(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data['lot_id'] = UUID(data['lot_id'])
        data["execution_type"] = ExecutionType.to_enum(data["execution_type"])
        data["order_type"] = OrderType.to_enum(data["order_type"])
        data["time_in_force"] = TimeInForce.to_enum(data["time_in_force"])
        data = convert_floats(data, ["quantity", "price"])
        data = convert_dates(data, "time")

        return data
