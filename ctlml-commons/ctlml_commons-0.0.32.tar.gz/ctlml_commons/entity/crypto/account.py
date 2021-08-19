from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from ctlml_commons.entity.crypto.balance import Balance
from ctlml_commons.util.date_utils import date_parse, readable_datetime_to_str
from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class Rewards:
    apy: float
    formatted_apy: str
    label: str

    def serialize(self) -> Dict[str, Any]:
        data = deepcopy(self.__dict__)

        data = convert_floats(data, ["apy"])

        return data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> Optional[Rewards]:
        if data is None:
            return data
        return cls(**cls.clean(data))

    @classmethod
    def clean(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        data["apy"] = float(data["apy"])
        return data


@dataclass(frozen=True)
class Account:
    allow_deposits: bool
    allow_withdrawals: bool
    balance: Balance
    created_at: datetime
    currency: str
    id: str
    name: str
    native_balance: Balance
    primary: bool
    resource: str
    resource_path: str
    type: str
    updated_at: datetime
    rewards: Optional[Rewards] = None
    rewards_apy: Optional[float] = None

    def serialize(self) -> Dict[str, Any]:
        data = deepcopy(self.__dict__)

        if self.balance is not None:
            data["balance"] = self.balance.serialize()
        if self.native_balance is not None:
            data["native_balance"] = self.native_balance.serialize()
        if self.rewards is not None:
            data["rewards"] = self.rewards.serialize()

        if self.created_at is not None:
            data["created_at"] = readable_datetime_to_str(self.created_at)
        if self.updated_at is not None:
            data["updated_at"] = readable_datetime_to_str(self.updated_at)

        return data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> Account:
        if data is None:
            return data
        return cls(**cls.clean(data))

    @classmethod
    def clean(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        data["balance"] = Balance.deserialize(data["balance"])
        data["native_balance"] = Balance.deserialize(data["native_balance"])
        if "rewards" in data:
            data["rewards"] = Rewards.deserialize(data["rewards"])

        data["created_at"] = date_parse(data["created_at"])
        data["updated_at"] = date_parse(data["updated_at"])

        if "rewards_apy" in data and data["rewards_apy"] is not None:
            data["rewards_apy"] = float(data["rewards_apy"])
        return data
