from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from ctlml_commons.util.date_utils import convert_dates, readable_datetime_to_str


@dataclass(frozen=True)
class Address:
    address: str
    address_info: Dict[str, str]
    callback_url: Optional[str]
    created_at: datetime
    deposit_uri: str
    id: str
    name: Optional[str]
    network: str
    resource: str
    resource_path: str
    updated_at: datetime
    uri_scheme: str
    warnings: List[Any]

    def serialize(self) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(self.__dict__)

        data['created_at'] = readable_datetime_to_str(self.created_at)
        data['updated_at'] = readable_datetime_to_str(self.updated_at)

        return data

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Address:
        return cls(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data = convert_dates(data)

        return data
