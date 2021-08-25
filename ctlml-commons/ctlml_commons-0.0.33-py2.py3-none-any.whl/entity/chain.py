from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from ctlml_commons.entity.tick import Tick
from ctlml_commons.util.date_utils import date_parse
from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class Chain:
    id: str
    symbol: str
    can_open_position: bool
    cash_component: str
    expiration_dates: List[datetime]
    trade_value_multiplier: float
    underlying_instruments: List[UnderlyingInstruments]
    min_ticks: Tick

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Chain:
        return Chain(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["expiration_dates"] = [date_parse(d) for d in data["expiration_dates"]]
        data["underlying_instruments"] = [UnderlyingInstruments.deserialize(u) for u in data["underlying_instruments"]]
        data["min_ticks"] = Tick.deserialize(data["min_ticks"])

        data = convert_floats(data, ["trade_value_multiplier"])

        return data


@dataclass(frozen=True)
class UnderlyingInstruments:
    id: str
    instrument: str
    quantity: float

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> UnderlyingInstruments:
        return UnderlyingInstruments(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data = convert_floats(data, ["quantity"])

        return data
