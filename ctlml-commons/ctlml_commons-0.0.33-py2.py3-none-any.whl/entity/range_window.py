from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict

from ctlml_commons.util.num_utils import convert_floats


@dataclass(frozen=True)
class RangeWindow:
    floor: float
    ceiling: float

    def serialize(self) -> Dict[str, Any]:
        return deepcopy(self.__dict__)

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> RangeWindow:
        return RangeWindow(**cls.clean(input_data))

    @classmethod
    def clean(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(input_data)
        data = convert_floats(data, ["ceiling", "floor"])

        return data