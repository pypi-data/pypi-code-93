from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Balance:
    amount: float
    currency: str

    def serialize(self) -> Dict[str, Any]:
        return deepcopy(self.__dict__)

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> Optional[Balance]:
        if data is None:
            return data
        return cls(**cls.clean(data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data["amount"] = float(data["amount"])
        return data
