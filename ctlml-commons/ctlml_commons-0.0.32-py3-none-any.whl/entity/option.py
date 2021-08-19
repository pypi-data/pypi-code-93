from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from ctlml_commons.entity.option_type import OptionType
from ctlml_commons.entity.state import State
from ctlml_commons.entity.tick import Tick
from ctlml_commons.entity.tradability import Tradability
from ctlml_commons.util.date_utils import convert_dates
from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class Option:
    chain_id: str
    chain_symbol: str
    created_at: datetime
    expiration_date: datetime
    id: str
    issue_date: datetime
    min_ticks: Tick
    rhs_tradability: Tradability
    state: State
    strike_price: float
    tradability: Tradability
    type: OptionType
    updated_at: datetime
    url: str
    sellout_datetime: datetime
    adjusted_mark_price: Optional[float] = None
    ask_price: Optional[float] = None
    ask_size: Optional[int] = None
    bid_price: Optional[float] = None
    bid_size: Optional[int] = None
    break_even_price: Optional[float] = None
    high_price: Optional[float] = None
    instrument: Optional[str] = None
    last_trade_price: Optional[float] = None
    last_trade_size: Optional[int] = None
    low_price: Optional[float] = None
    mark_price: Optional[float] = None
    open_interest: Optional[int] = None
    previous_close_date: Optional[datetime] = None
    previous_close_price: Optional[float] = None
    volume: Optional[int] = None
    chance_of_profit_long: Optional[float] = None
    chance_of_profit_short: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    implied_volatility: Optional[float] = None
    rho: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    high_fill_rate_buy_price: Optional[float] = None
    high_fill_rate_sell_price: Optional[float] = None
    low_fill_rate_buy_price: Optional[float] = None
    low_fill_rate_sell_price: Optional[float] = None

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Option:
        return Option(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["min_ticks"] = Tick.deserialize(input_data=data["min_ticks"])
        data["rhs_tradability"] = Tradability.to_enum(data["rhs_tradability"])
        data["state"] = State.to_enum(data["state"])
        data["tradability"] = Tradability.to_enum(data["tradability"])
        data["type"] = OptionType.to_enum(data["type"])

        data = convert_floats(
            data,
            [
                "strike_price",
                "adjusted_mark_price",
                "ask_price",
                "ask_size",
                "bid_price",
                "bid_size",
                "break_even_price",
                "high_price",
                "last_trade_price",
                "last_trade_size",
                "low_price",
                "mark_price",
                "open_interest",
                "previous_close_price",
                "volume",
                "chance_of_profit_long",
                "chance_of_profit_short",
                "delta",
                "gamma",
                "implied_volatility",
                "rho",
                "theta",
                "vega",
                "high_fill_rate_buy_price",
                "high_fill_rate_sell_price",
                "low_fill_rate_buy_price",
                "low_fill_rate_sell_price",
            ],
        )

        data = convert_dates(data, "expiration_date", "issue_date", "sellout_datetime", "previous_close_date")

        return data
