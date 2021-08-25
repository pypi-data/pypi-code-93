from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class Price:
    amount: float
    currency_code: Optional[str] = None
    currency_id: Optional[str] = None

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Price:
        return Price(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data = convert_floats(data, ["amount"])

        return data
