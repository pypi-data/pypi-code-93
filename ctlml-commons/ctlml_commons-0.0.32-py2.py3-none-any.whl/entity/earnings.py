from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from ctlml_commons.util.date_utils import convert_dates
from ctlml_commons.util.num_utils import convert_floats

EXAMPLE: List[Dict[str, Any]] = [
    {
        "symbol": "MRO",
        "instrument": "https://api.robinhood.com/instruments/ab4f79fc-f84a-4f7b-8132-4f3e5fb38075/",
        "year": 2018,
        "quarter": 3,
        "eps": {"estimate": "0.210000", "actual": "0.240000"},
        "report": {"date": "2018-11-07", "timing": "pm", "verified": True},
        "call": None,
    },
    {
        "symbol": "MRO",
        "instrument": "https://api.robinhood.com/instruments/ab4f79fc-f84a-4f7b-8132-4f3e5fb38075/",
        "year": 2018,
        "quarter": 4,
        "eps": {"estimate": "0.150000", "actual": "0.150000"},
        "report": {"date": "2019-02-13", "timing": "pm", "verified": True},
        "call": None,
    },
    {
        "symbol": "MRO",
        "instrument": "https://api.robinhood.com/instruments/ab4f79fc-f84a-4f7b-8132-4f3e5fb38075/",
        "year": 2019,
        "quarter": 1,
        "eps": {"estimate": "0.060000", "actual": "0.310000"},
        "report": {"date": "2019-05-01", "timing": "pm", "verified": True},
        "call": None,
    },
    {
        "symbol": "MRO",
        "instrument": "https://api.robinhood.com/instruments/ab4f79fc-f84a-4f7b-8132-4f3e5fb38075/",
        "year": 2019,
        "quarter": 2,
        "eps": {"estimate": "0.150000", "actual": "0.230000"},
        "report": {"date": "2019-08-07", "timing": "pm", "verified": True},
        "call": {
            "datetime": "2019-08-08T13:00:00Z",
            "broadcast_url": None,
            "replay_url": "http://mmm.wallstreethorizon.com/u.asp?u=231423",
        },
    },
    {
        "symbol": "MRO",
        "instrument": "https://api.robinhood.com/instruments/ab4f79fc-f84a-4f7b-8132-4f3e5fb38075/",
        "year": 2019,
        "quarter": 3,
        "eps": {"estimate": "0.070000", "actual": "0.140000"},
        "report": {"date": "2019-11-06", "timing": "pm", "verified": True},
        "call": {
            "datetime": "2019-11-07T14:00:00Z",
            "broadcast_url": None,
            "replay_url": "http://mmm.wallstreethorizon.com/u.asp?u=295100",
        },
    },
    {
        "symbol": "MRO",
        "instrument": "https://api.robinhood.com/instruments/ab4f79fc-f84a-4f7b-8132-4f3e5fb38075/",
        "year": 2019,
        "quarter": 4,
        "eps": {"estimate": "0.100000", "actual": "0.070000"},
        "report": {"date": "2020-02-12", "timing": "pm", "verified": True},
        "call": {
            "datetime": "2020-02-13T14:00:00Z",
            "broadcast_url": None,
            "replay_url": "http://mmm.wallstreethorizon.com/u.asp?u=307075",
        },
    },
    {
        "symbol": "MRO",
        "instrument": "https://api.robinhood.com/instruments/ab4f79fc-f84a-4f7b-8132-4f3e5fb38075/",
        "year": 2020,
        "quarter": 1,
        "eps": {"estimate": "-0.140000", "actual": "-0.160000"},
        "report": {"date": "2020-05-06", "timing": "pm", "verified": True},
        "call": {
            "datetime": "2020-05-07T13:00:00Z",
            "broadcast_url": None,
            "replay_url": "http://mmm.wallstreethorizon.com/u.asp?u=307075",
        },
    },
    {
        "symbol": "MRO",
        "instrument": "https://api.robinhood.com/instruments/ab4f79fc-f84a-4f7b-8132-4f3e5fb38075/",
        "year": 2020,
        "quarter": 2,
        "eps": {"estimate": None, "actual": None},
        "report": {"date": "2020-08-05", "timing": "pm", "verified": False},
        "call": None,
    },
]


@dataclass(frozen=True)
class Earnings:
    symbol: str
    instrument: str
    year: int
    quarter: int
    eps: EarningsPerShare
    report: EarningsReport
    call: EarningsCall

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Earnings:
        return Earnings(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["eps"] = EarningsPerShare.deserialize(data["eps"])
        data["report"] = EarningsReport.deserialize(data["report"]) if data["report"] is not None else None
        data["call"] = EarningsCall.deserialize(data["call"]) if data["call"] is not None else None

        return data


@dataclass(frozen=True)
class EarningsPerShare:
    estimate: float
    actual: float

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> EarningsPerShare:
        return EarningsPerShare(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return convert_floats(input_data, ["estimate", "actual"], 0.00)


@dataclass(frozen=True)
class EarningsReport:
    date: datetime
    timing: str
    verified: bool

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> EarningsReport:
        return EarningsReport(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return convert_dates(input_data, "date")


@dataclass(frozen=True)
class EarningsCall:
    datetime: datetime
    broadcast_url: Optional[str]
    replay_url: Optional[str]

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> EarningsCall:
        return EarningsCall(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return convert_dates(input_data, "datetime")
