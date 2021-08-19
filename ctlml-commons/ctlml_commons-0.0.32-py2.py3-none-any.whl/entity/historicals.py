from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from ctlml_commons.util.date_utils import convert_dates
from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class Historicals:
    begins_at: datetime
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: int
    session: str
    interpolated: bool
    symbol: str

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Historicals:
        return Historicals(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data = convert_floats(data, ["open_price", "close_price", "high_price", "low_price"])
        data = convert_dates(data, "begins_at")

        return data
