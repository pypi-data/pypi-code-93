from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict

from ctlml_commons.entity.state import State


@dataclass
class Status:
    state: State
    message: str

    def serialize(self) -> Dict[str, Any]:
        data: Dict[str, Any] = deepcopy(self.__dict__)

        data['state'] = self.state.value()

        return data

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> Status:
        data = deepcopy(input_data)

        data["state"] = State.to_enum(data["state"])

        return cls(**data)
