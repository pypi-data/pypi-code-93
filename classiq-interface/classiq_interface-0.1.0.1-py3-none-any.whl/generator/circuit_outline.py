import pydantic
from typing import TypeVar

Qubit = TypeVar("Qubit", bound=pydantic.conint(ge=0))
Cycle = TypeVar("Cycle", bound=pydantic.conint(ge=0))
Clbit = TypeVar("Clbit", bound=pydantic.conint(ge=0))
