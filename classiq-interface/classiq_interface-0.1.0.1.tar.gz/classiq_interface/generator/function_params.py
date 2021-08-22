import abc
from enum import Enum
from typing import Optional, ClassVar, Type, Any

import pydantic


class DefaultInputNames(Enum):
    pass


class DefaultOutputNames(Enum):
    OUT = "OUT"


class IO(Enum):
    Input = "Input"
    Output = "Output"


class FunctionParams(pydantic.BaseModel, abc.ABC):
    _input_names: Type[Enum] = pydantic.PrivateAttr(default=DefaultInputNames)
    _output_names: Type[Enum] = pydantic.PrivateAttr(default=DefaultOutputNames)

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.create_io_enums()

    def get_io_enum(self, io: IO) -> Type[Enum]:
        if io == IO.Input:
            return self._input_names
        if io == IO.Output:
            return self._output_names

    def create_io_enums(self):
        pass

    def is_valid_io_name(self, name: str, io: IO) -> bool:
        return name in self.get_io_enum(io).__members__
