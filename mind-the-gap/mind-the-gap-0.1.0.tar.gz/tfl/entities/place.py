from __future__ import annotations

from dataclasses import dataclass
from typing import List

from tfl.entities.additional_property import AdditionalProperty


@dataclass
class Place:
    id: str
    url: str
    commonName: str
    placeType: str
    additionalProperties: List[AdditionalProperty]
    children: List[Place]
    childrenUrls: List[str]
    lat: float
    lon: float
