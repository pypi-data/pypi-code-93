from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from ctlml_commons.entity.option_type import OptionType
from ctlml_commons.util.date_utils import convert_dates
from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class AggregatePosition:
    id: str
    chain: str
    symbol: str
    strategy: str
    average_open_price: float
    legs: List[Leg]
    quantity: float
    intraday_average_open_price: float
    intraday_quantity: float
    direction: str
    intraday_direction: str
    trade_value_multiplier: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> AggregatePosition:
        return AggregatePosition(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["legs"] = [Leg.deserialize(leg) for leg in data["legs"]]

        data = convert_floats(
            data,
            [
                "average_open_price",
                "quantity",
                "intraday_average_open_price",
                "intraday_quantity",
                "trade_value_multiplier",
            ],
        )

        data = convert_dates(data)

        return data


@dataclass(frozen=True)
class Leg:
    id: str
    position: str
    position_type: str  # TODO: enum
    option: str
    ratio_quantity: int
    expiration_date: datetime
    strike_price: float
    option_type: OptionType

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Leg:
        return Leg(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["option_type"] = OptionType.to_enum(data["option_type"])

        data = convert_floats(data, ["strike_price"])
        data = convert_dates(data, "expiration_date")

        return data
