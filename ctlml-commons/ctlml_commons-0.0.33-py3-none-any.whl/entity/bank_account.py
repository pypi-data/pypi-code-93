from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from ctlml_commons.util.date_utils import convert_dates
from ctlml_commons.util.entity_utils import separate_fields


@dataclass(frozen=True)
class BankAccount:
    id: str
    verification_method: str
    bank_account_holder_name: str
    bank_account_type: str
    bank_account_number: str
    bank_routing_number: str
    bank_account_nickname: str
    verified: bool
    state: str  # TODO: enum
    first_created_at: datetime
    url: str
    withdrawal_limit: str
    initial_deposit: str
    account: str
    unlink: str
    created_at: datetime
    document_request: Optional[Any] = None
    verify_micro_deposits: Optional[Any] = None
    unlinked_at: Optional[Any] = None
    other: Dict[str, str] = field(default_factory=dict)

    def serialize(self) -> Dict[str, Any]:
        return deepcopy(self.__dict__)

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> BankAccount:
        known, other = cls.separate(cls.clean(input_data=input_data))

        return cls(**known, other=other)

    @classmethod
    def separate(cls, input_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        return separate_fields(known_fields=cls.__dataclass_fields__.keys(), input_data=input_data)

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data = convert_dates(data, "first_created_at")

        return data
