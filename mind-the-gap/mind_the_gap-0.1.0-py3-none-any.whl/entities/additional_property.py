from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AdditionalProperty:
    category: str
    key: str
    sourceSystemKey: str
    value: str
    modified: str
