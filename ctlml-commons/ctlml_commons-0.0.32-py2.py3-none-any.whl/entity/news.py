from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Tuple

from ctlml_commons.util.date_utils import convert_dates
from ctlml_commons.util.entity_utils import separate_fields


@dataclass(frozen=True)
class News:
    api_source: str
    author: str
    num_clicks: int
    preview_image_url: str
    published_at: datetime
    relay_url: str
    source: str
    summary: str
    title: str
    updated_at: datetime
    url: str
    uuid: str
    related_instruments: List[str]
    preview_text: str
    currency_id: str
    other: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> News:
        known, other = cls.separate(cls.clean(input_data=input_data))

        return cls(**known, other=other)

    @classmethod
    def separate(cls, input_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        return separate_fields(known_fields=cls.__dataclass_fields__.keys(), input_data=input_data)

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data = convert_dates(data, "published_at")

        return data
