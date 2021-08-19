from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict

from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class Tick:
    above_tick: float
    below_tick: float
    cutoff_price: float

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Tick:
        return Tick(**cls.clean(input_data=input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)

        data = convert_floats(data, ["above_tick", "below_tick", "cutoff_price"])

        return data
