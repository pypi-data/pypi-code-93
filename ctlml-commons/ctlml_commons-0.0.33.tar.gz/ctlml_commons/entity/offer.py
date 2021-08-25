from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List

from ctlml_commons.entity.price import Price
from ctlml_commons.entity.printable import Printable
from ctlml_commons.util.date_utils import convert_dates


@dataclass(frozen=True)
class Offers:
    asks: List[Offer]
    bids: List[Offer]
    instrument_id: str
    updated_at: datetime

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Offers:
        return cls(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["asks"] = [Offer.deserialize(input_data=o) for o in data["asks"]]
        data["bids"] = [Offer.deserialize(input_data=o) for o in data["bids"]]

        data = convert_dates(data)

        return data


@dataclass(frozen=True)
class Offer:
    side: str
    price: Price
    quantity: int

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Offer:
        return Offer(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["price"] = Price.deserialize(input_data=data["price"])

        return data


class OfferType(Printable, Enum):
    ASK = auto()
    BID = auto()

    @staticmethod
    def to_enum(value: str) -> OfferType:
        v: str = value.upper()
        return OfferType[v]
