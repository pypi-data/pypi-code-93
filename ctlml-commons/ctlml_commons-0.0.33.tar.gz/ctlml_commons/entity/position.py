from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Tuple

from ctlml_commons.util.date_utils import convert_dates, datetime_to_str
from ctlml_commons.util.entity_utils import separate_fields
from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    intraday_quantity: float
    created_at: datetime
    updated_at: datetime
    average_buy_price: float
    pending_average_buy_price: float
    intraday_average_buy_price: float
    instrument: str
    shares_available_for_exercise: float
    shares_held_for_buys: float
    shares_held_for_options_collateral: float
    shares_held_for_options_events: float
    shares_held_for_sells: float
    shares_held_for_stock_grants: float
    shares_pending_from_options_events: float
    url: str
    account: str
    account_number: str
    shares_available_for_closing_short_position: float = 0.00
    other: Dict[str, str] = field(default_factory=dict)

    def serialize(self) -> Dict[str, Any]:
        data = deepcopy(self.__dict__)

        for a_date in ["created_at", "updated_at"]:
            data[a_date] = datetime_to_str(data[a_date])

        return data

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Position:
        known, other = cls.separate(cls.clean(input_data=input_data))

        return cls(**known, other=other)

    @classmethod
    def separate(cls, input_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        return separate_fields(known_fields=cls.__dataclass_fields__.keys(), input_data=input_data)

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data = convert_floats(
            data,
            [
                "quantity",
                "intraday_quantity",
                "average_buy_price",
                "pending_average_buy_price",
                "intraday_average_buy_price",
                "shares_available_for_closing_short_position",
                "shares_available_for_exercise",
                "shares_held_for_buys",
                "shares_held_for_options_collateral",
                "shares_held_for_options_events",
                "shares_held_for_sells",
                "shares_held_for_stock_grants",
                "shares_pending_from_options_events",
            ],
        )

        data = convert_dates(data)

        return data
