from __future__ import annotations

from dataclasses import dataclass
from typing import List

from tfl.api.presentation.entities.place import Place


@dataclass
class PlacesResponse:
    centrePoint: List[float]
    places: List[Place]
