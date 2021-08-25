from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from ctlml_commons.util.date_utils import convert_dates
from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class Mover:
    instrument_url: str
    symbol: str
    updated_at: datetime
    price_movement: PriceMovement
    description: str

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["price_movement"] = PriceMovement.deserialize(input_data=data["price_movement"])

        data = convert_dates(data)

        return data

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Mover:
        return Mover(**cls.clean(input_data=input_data))


@dataclass(frozen=True)
class PriceMovement:
    market_hours_last_movement_pct: float
    market_hours_last_price: float

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data = convert_floats(data, ["market_hours_last_movement_pct", "market_hours_last_price"])

        return data

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> PriceMovement:
        return PriceMovement(**cls.clean(input_data=input_data))
