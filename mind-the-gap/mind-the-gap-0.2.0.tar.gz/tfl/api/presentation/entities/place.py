from __future__ import annotations

from dataclasses import dataclass
from typing import List

from tfl.api.presentation.entities.additional_properties import AdditionalProperties


@dataclass
class Place:
    id: str
    url: str
    commonName: str
    placeType: str
    additionalProperties: List[AdditionalProperties]
    children: List[Place]
    childrenUrls: List[str]
    lat: float
    lon: float
