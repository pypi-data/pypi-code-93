from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict

from ctlml_commons.entity.state import State
from ctlml_commons.util.date_utils import convert_dates
from ctlml_commons.util.num_utils import convert_floats


class TransferDirection(Enum):
    DEPOSIT = auto()

    @staticmethod
    def to_enum(value: str) -> TransferDirection:
        v: str = value.upper().replace(" ", "-").replace("-", "_")
        return TransferDirection[v]

    def value(self) -> str:
        return self.name.lower()


@dataclass(frozen=True)
class BankTransfer:
    id: str
    ref_id: str
    url: str
    cancel: str
    ach_relationship: str
    account: str
    amount: float
    direction: TransferDirection
    state: State
    fees: float
    status_description: str
    scheduled: bool
    expected_landing_date: datetime
    early_access_amount: float
    created_at: datetime
    updated_at: datetime
    rhs_state: State
    expected_sweep_at: str
    expected_landing_datetime: datetime
    investment_schedule_id: str

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> BankTransfer:
        return BankTransfer(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["direction"] = TransferDirection.to_enum(data["direction"])
        data["state"] = State.to_enum(data["state"])
        data["rhs_state"] = State.to_enum(data["rhs_state"])

        data = convert_floats(data, ["amount", "fees", "early_access_amount"])

        data = convert_dates(data, "expected_landing_date", "expected_landing_datetime")

        return data
