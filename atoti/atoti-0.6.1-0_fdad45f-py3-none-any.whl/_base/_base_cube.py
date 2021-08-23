from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic, Tuple, TypeVar

from .._bitwise_operators_only import IdentityElement
from .._repr_utils import ReprJson, ReprJsonable
from ._base_hierarchies import _BaseHierarchies
from ._base_levels import _Levels
from ._base_measures import _Measures

_BaseCube = TypeVar("_BaseCube", bound="BaseCube")


@dataclass(frozen=True)
class BaseCube(Generic[_BaseHierarchies, _Levels, _Measures], ReprJsonable):
    """Base cube."""

    _name: str
    _hierarchies: _BaseHierarchies
    _measures: _Measures

    @property
    def name(self) -> str:
        """Name of the cube."""
        return self._name

    @property
    @abstractmethod
    def levels(self) -> _Levels:
        """Levels of the cube."""

    @property
    def measures(self) -> _Measures:
        """Measures of the cube."""
        return self._measures

    @property
    def hierarchies(self) -> _BaseHierarchies:
        """Hierarchies of the cube."""
        return self._hierarchies

    def _repr_json_(self) -> ReprJson:
        return (
            {
                "Dimensions": self.hierarchies._repr_json_()[0],
                "Measures": self.measures._repr_json_()[0],
            },
            {"expanded": False, "root": self.name},
        )

    def _identity(self) -> Tuple[IdentityElement, ...]:
        return (self._name,)
