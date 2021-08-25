from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from ctlml_commons.util.date_utils import convert_dates, datetime_to_str
from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class Lot:
    """Uniquely identifies an ingress execution, i.e. BUY 10 of ABCD at LIMIT price of 0.1."""

    id: UUID  # Internal id
    symbol: str  # Ticker
    shares: float  # Shares
    purchase_price: float  # Price per share
    notes: str  # Summary of why this lot was created
    investment_strategy_data: str
    purchase_time: datetime  # Purchase time
    b_id: Optional[UUID] = None  # Brokerage external id

    def serialize(self) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(self.__dict__)

        for field in ["id", "b_id"]:
            data[field] = str(data[field])

        data["purchase_time"] = datetime_to_str(self.purchase_time)

        return data

    def add_brokerage_id(self, b_id: UUID) -> Lot:
        return Lot(
            id=self.id,
            symbol=self.symbol,
            shares=self.shares,
            purchase_price=self.purchase_price,
            notes=self.notes,
            purchase_time=self.purchase_time,
            investment_strategy_data=self.investment_strategy_data,
            b_id=b_id,
        )

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Lot:
        return Lot(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        for field in ["id", "b_id"]:
            data[field] = UUID(data[field])

        data = convert_floats(data, ["shares"])
        data = convert_dates(data, "purchase_time")

        return data
