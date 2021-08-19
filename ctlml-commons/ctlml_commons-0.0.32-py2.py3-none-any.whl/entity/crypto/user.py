from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from ctlml_commons.util.date_utils import convert_dates


@dataclass(frozen=True)
class Country:
    code: str
    is_in_europe: bool
    name: str

    def serialize(self) -> Dict[str, Any]:
        return deepcopy(self.__dict__)

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Country:
        return cls(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(input_data)

        data["is_in_europe"] = bool(data["is_in_europe"])

        return data


@dataclass(frozen=True)
class Nationality:
    code: str
    name: str

    def serialize(self) -> Dict[str, Any]:
        return deepcopy(self.__dict__)

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Nationality:
        return cls(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(input_data)

        return data


@dataclass(frozen=True)
class Referral:
    amount: float
    currency: str
    currency_symbol: str
    referral_threshold: float

    def serialize(self) -> Dict[str, Any]:
        return deepcopy(self.__dict__)

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Referral:
        return cls(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(input_data)

        data["amount"] = float(data["amount"])
        data["referral_threshold"] = float(data["referral_threshold"])

        return data


@dataclass(frozen=True)
class Tiers:
    body: Optional[str]
    completed_description: Optional[str]
    header: Optional[str]
    upgrade_button_text: Optional[str]

    def serialize(self) -> Dict[str, Any]:
        return deepcopy(self.__dict__)

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Tiers:
        return cls(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(input_data)

        return data


@dataclass(frozen=True)
class User:
    avatar_url: str
    bitcoin_unit: str
    country: Country
    created_at: datetime
    has_blocking_buy_restrictions: bool
    has_buy_deposit_payment_methods: bool
    has_made_a_purchase: bool
    has_unverified_buy_deposit_payment_methods: bool
    id: str
    legacy_id: str
    name: str
    nationality: Nationality
    native_currency: str
    needs_kyc_remediation: bool
    profile_bio: Optional[Any]
    profile_location: Optional[Any]
    profile_url: Optional[Any]
    referral_money: Referral
    region_supports_crypto_to_crypto_transfers: bool
    region_supports_fiat_transfers: bool
    resource: str
    resource_path: str
    show_instant_ach_ux: bool
    state: str
    supports_rewards: bool
    tiers: Tiers
    time_zone: str
    user_type: str
    username: Optional[str]

    def serialize(self) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(self.__dict__)

        if self.country is not None:
            data["country"] = self.country.serialize()
        if self.nationality is not None:
            data["nationality"] = self.nationality.serialize()
        if self.referral_money is not None:
            data["referral_money"] = self.referral_money.serialize()
        if self.tiers is not None:
            data["tiers"] = self.tiers.serialize()

        return data

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> User:
        return cls(**cls.clean(input_data=input_data))

    @staticmethod
    def clean(input_data: Dict[str, Any]) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(input_data)

        data = convert_dates(data)

        data["country"] = Country.deserialize(data["country"])
        data["nationality"] = Nationality.deserialize(data["nationality"])
        data["referral_money"] = Referral.deserialize(data["referral_money"])
        data["tiers"] = Tiers.deserialize(data["tiers"])

        return data
