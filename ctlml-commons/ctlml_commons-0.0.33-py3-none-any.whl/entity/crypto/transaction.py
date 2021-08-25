from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional, Tuple

from ctlml_commons.entity.crypto.balance import Balance
from ctlml_commons.util.date_utils import date_parse
from ctlml_commons.util.entity_utils import separate_fields


@dataclass(frozen=True)
class TransactionDestination:
    address: str
    address_url: str
    currency: str
    resource: str
    address_info: Optional[TransactionDestinationInfo] = None

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> TransactionDestination:
        return cls(**cls.clean(data))

    @classmethod
    def clean(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if "address_info" in data:
            data["address_info"] = TransactionDestinationInfo.deserialize(data["address_info"])

        return data


@dataclass(frozen=True)
class TransactionDestinationInfo:
    address: str

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> TransactionDestinationInfo:
        return cls(**data)


@dataclass(frozen=True)
class TransactionSource:
    id: Optional[str] = None
    resource: Optional[str] = None
    resource_path: Optional[str] = None
    currency: Optional[str] = None

    def serialize(self) -> Dict[str, Any]:
        return deepcopy(self.__dict__)

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> TransactionSource:
        return cls(**data)


class TransactionHealth(Enum):
    POSITIVE = auto()

    @staticmethod
    def to_enum(value: str) -> TransactionHealth:
        t: str = value.upper()
        return TransactionHealth[t]

    def value(self) -> str:
        return self.name.lower()

    def serialize(self) -> str:
        return self.value()


@dataclass(frozen=True)
class TransactionDetails:
    header: str
    health: TransactionHealth
    subtitle: str
    title: str
    payment_method_name: Optional[str] = None

    def serialize(self) -> Dict[str, Any]:
        data = deepcopy(self.__dict__)

        data["health"] = self.health.serialize()

        return data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> TransactionDetails:
        return cls(**cls.clean(data))

    @classmethod
    def clean(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        data["health"] = TransactionHealth.to_enum(data["health"])

        return data


class TransactionType(Enum):
    BUY = auto()
    EXCHANGE_DEPOSIT = auto()
    FIAT_DEPOSIT = auto()
    INFLATION_REWARD = auto()
    INTEREST = auto()
    PRO_WITHDRAWAL = auto()
    SEND = auto()
    STAKING_REWARD = auto()
    TRADE = auto()

    @staticmethod
    def to_enum(value: str) -> TransactionType:
        t: str = value.upper()
        return TransactionType[t]

    def value(self) -> str:
        return self.name.lower()

    def serialize(self) -> str:
        return self.value()


class TransactionResource(Enum):
    TRANSACTION = auto()

    @staticmethod
    def to_enum(value: str) -> TransactionResource:
        t: str = value.upper()
        return TransactionResource[t]

    def value(self) -> str:
        return self.name.lower()

    def serialize(self) -> str:
        return self.value()


class TransactionStatus(Enum):
    COMPLETED = auto()
    CONFIRMED = auto()
    OFF_BLOCKCHAIN = auto()

    @staticmethod
    def to_enum(value: str) -> TransactionStatus:
        t: str = value.upper()
        return TransactionStatus[t]

    def value(self) -> str:
        return self.name.lower()

    def serialize(self) -> str:
        return self.value()


@dataclass(frozen=True)
class Network:
    status: TransactionStatus
    status_description: str
    hash: Optional[str] = None
    transaction_url: Optional[str] = None
    confirmations: Optional[str] = None
    transaction_amount: Optional[Balance] = None
    transaction_fee: Optional[Balance] = None

    def serialize(self) -> Dict[str, Any]:
        data = deepcopy(self.__dict__)

        data["status"] = self.status.serialize()

        return data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> Network:
        return cls(**cls.clean(data))

    @classmethod
    def clean(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        data["status"] = TransactionStatus.to_enum(data["status"])

        for field in ["transaction_amount", "transaction_fee"]:
            if field in data:
                data[field] = Balance.deserialize(data[field])

        return data


@dataclass(frozen=True)
class Transaction:
    id: str
    amount: Balance
    native_amount: Balance
    type: TransactionType
    status: TransactionStatus
    resource: TransactionResource
    details: TransactionDetails
    created_at: datetime
    updated_at: datetime
    resource_path: str
    description: Optional[str] = None
    instant_exchange: Optional[bool] = False
    off_chain_status: Optional[TransactionStatus] = None
    network: Optional[Network] = None
    source: Optional[TransactionSource] = None
    buy: Optional[TransactionSource] = None
    trade: Optional[TransactionSource] = None
    from_source: Optional[TransactionSource] = None
    fiat_deposit: Optional[TransactionSource] = None
    application: Optional[TransactionSource] = None
    to: Optional[TransactionDestination] = None
    idem: Optional[str] = None
    hide_native_amount: Optional[bool] = None
    other: Dict[str, str] = field(default_factory=dict)


    def serialize(self) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(self.__dict__)

        for field_name in ["type", "status", "resource", "details", "from_source", "off_chain_status", "network"]:
            if field_name in data and data[field_name] is not None:
                data[field_name] = getattr(self, field_name).serialize()

        del data["from_source"]

        return data

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Transaction:
        known, other = cls.separate(cls.clean(input_data=input_data))

        return cls(**known, other=other)

    @classmethod
    def separate(cls, input_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        return separate_fields(known_fields=cls.__dataclass_fields__.keys(), input_data=input_data)

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["amount"] = Balance.deserialize(data["amount"])
        data["native_amount"] = Balance.deserialize(data["native_amount"])
        data["details"] = TransactionDetails.deserialize(data["details"])

        data["type"] = TransactionType.to_enum(data["type"])
        data["status"] = TransactionStatus.to_enum(data["status"])

        if "off_chain_status" in data:
            data["off_chain_status"] = TransactionStatus.to_enum(data["off_chain_status"])

        data["resource"] = TransactionResource.to_enum(data["resource"])

        for source in ["application", "buy", "fiat_deposit", "from", "trade"]:
            if source in data:
                data[source] = TransactionSource.deserialize(data[source])

                if source in ["from"]:
                    data["from_source"] = data[source]
                    del data[source]

        data["created_at"] = date_parse(data["created_at"])
        data["updated_at"] = date_parse(data["updated_at"])

        if "network" in data:
            data["network"] = Network.deserialize(data["network"])
        return data
