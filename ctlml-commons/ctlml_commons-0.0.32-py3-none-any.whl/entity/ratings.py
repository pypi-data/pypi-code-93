from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List

from ctlml_commons.entity.printable import Printable
from ctlml_commons.util.date_utils import convert_dates


@dataclass(frozen=True)
class Ratings:
    summary: Dict[RatingType, int]
    ratings: List[Rating]
    instrument_id: str
    ratings_published_at: datetime

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Ratings:
        return Ratings(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["ratings"] = [Rating.deserialize(r) for r in data["ratings"]]

        # Map summary keys to RatingType enum
        mapping = {
            "num_buy_ratings": RatingType.BUY,
            "num_hold_ratings": RatingType.HOLD,
            "num_sell_ratings": RatingType.SELL,
        }

        summary: Dict[RatingType, int] = {}
        for summary_key, value in data["summary"].items():
            if summary_key in mapping.keys():
                summary[mapping[summary_key]] = value
            else:
                print(f"WARNING: Rating Summary Type: {summary_key} not found.")
        data["summary"] = summary

        data = convert_dates(data, "ratings_published_at")

        return data


@dataclass(frozen=True)
class Rating:
    published_at: datetime
    type: RatingType
    text: str

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Rating:
        return Rating(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["type"] = RatingType.to_enum(data["type"])

        data = convert_dates(data, "published_at")

        return data


class RatingType(Printable, Enum):
    BUY = auto()
    SELL = auto()
    HOLD = auto()

    @staticmethod
    def to_enum(value: str) -> RatingType:
        v: str = value.upper()
        return RatingType[v]
