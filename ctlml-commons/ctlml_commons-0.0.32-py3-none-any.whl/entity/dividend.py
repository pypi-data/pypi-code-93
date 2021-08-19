from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional

from ctlml_commons.entity.price import Price
from ctlml_commons.entity.printable import Printable
from ctlml_commons.util.date_utils import convert_dates
from ctlml_commons.util.num_utils import convert_floats


class DividendState(Printable, Enum):
    PAID = auto()
    PENDING = auto()
    REINVESTED = auto()
    VOIDED = auto()
    UNKNOWN = auto()

    @staticmethod
    def to_enum(value: str) -> Optional[DividendState]:
        if value is None:
            return DividendState.UNKNOWN
        v: str = value.upper().replace(" ", "-").replace("-", "_")
        return DividendState[v]

    def value(self) -> str:
        return self.name.lower()


@dataclass(frozen=True)
class Dividend:
    id: str
    url: str
    account: str
    instrument: str
    amount: float
    rate: float
    position: float
    withholding: float
    record_date: datetime
    payable_date: datetime
    paid_at: datetime
    state: DividendState
    nra_withholding: str
    drip_enabled: bool
    drip_order_id: Optional[str] = None
    drip_order_state: Optional[str] = None
    drip_order_quantity: Optional[float] = None
    drip_order_execution_price: Optional[Price] = None

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Dividend:
        return Dividend(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(input_data)

        data["drip_order_execution_price"] = (
            Price.deserialize(input_data=data["drip_order_execution_price"])
            if "drip_order_execution_price" in data
            else None
        )

        data["state"] = DividendState.to_enum(data["state"])
        data = convert_floats(data, ["amount", "rate", "position", "withholding", "drip_order_quantity"])
        data = convert_dates(data, "record_date", "payable_date", "paid_at")

        return data
