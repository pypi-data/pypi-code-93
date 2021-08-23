import operator
from abc import abstractmethod
from dataclasses import dataclass, field
from itertools import chain
from typing import (
    Any,
    Collection,
    Dict,
    Generic,
    Iterator,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

from typeguard import typeguard_ignore

from .._ipython_utils import ipython_key_completions_for_mapping
from .._repr_utils import ReprJson, ReprJsonable
from ._base_hierarchies import _BaseHierarchies
from ._base_hierarchy import BaseHierarchy
from ._base_level import _BaseLevel

_Levels = TypeVar("_Levels", bound="BaseLevels")
_LevelKey = Union[str, Tuple[str, str], Tuple[str, str, str]]


def _raise_multiple_levels_error(
    level_name: str, hierarchies: Collection[BaseHierarchy[Any]]
):
    error_msg = f"Multiple levels are named {level_name}. "
    error_msg += (
        "Use a tuple to specify the hierarchy (and the dimension if necessary): "
    )
    examples = [
        f'cube.levels[("{hierarchy.dimension}", "{hierarchy.name}", "{level_name}")]'
        for hierarchy in hierarchies
    ]
    error_msg += ", ".join(examples)
    raise KeyError(error_msg)


@typeguard_ignore
@dataclass(frozen=True)
class BaseLevels(
    Generic[_BaseLevel, _BaseHierarchies], Mapping[_LevelKey, _BaseLevel], ReprJsonable
):
    """Base class to manipulate flattened levels."""

    _hierarchies: _BaseHierarchies = field(repr=False)

    def _flatten(self) -> Mapping[str, Optional[_BaseLevel]]:
        flat_levels: Dict[str, Optional[_BaseLevel]] = dict()
        for hierarchy in self._hierarchies.values():
            for level in hierarchy.levels.values():
                if level.name in flat_levels:
                    # None is used as a flag to mark levels appearing in multiple hiearchies.
                    # When it happens, the user must use a tuple to retrieve the level.
                    # Like that: (hierarchy name, level name).
                    flat_levels[level.name] = None
                else:
                    flat_levels[level.name] = level
        return flat_levels

    def __getitem__(self, key: _LevelKey) -> _BaseLevel:
        """Return the level with the given key.

        Args:
            key: The name of the level, or a tuple like ``(hierarchy_name, level_name)``.

        Returns:
            The associated Level object

        """
        if isinstance(key, str):
            return self._find_level(key)

        if isinstance(key, tuple):
            if len(key) == 2:
                return self._find_level(key[1], hierarchy_name=key[0])
            if len(key) == 3:
                return self._find_level(
                    key[2], dimension_name=key[0], hierarchy_name=key[1]
                )
            raise TypeError(
                "Unexpected key of size %s, tuple must have a size of 2 or 3."
                % (len(key))
            )
        raise TypeError("Unexpected key of type %s" % (type(key)))

    @abstractmethod
    def _find_level(
        self,
        level_name: str,
        *,
        dimension_name: Optional[str] = None,
        hierarchy_name: Optional[str] = None,
    ) -> _BaseLevel:
        """Get a level from the hierarchy name and level name."""

    def __iter__(
        self,
    ) -> Iterator[_BaseLevel]:  # pyright: reportIncompatibleMethodOverride=false
        """Return the iterator on all the levels."""
        # Pyright can't match the type in the comprehension
        return chain(  # type: ignore
            *[
                iter(
                    {
                        (hierarchy.name, level_name): level
                        for level_name, level in hierarchy.levels.items()
                    }
                )
                for hierarchy in self._hierarchies.values()
            ]
        )

    def __len__(self):
        """Return the number of levels."""
        return sum([len(hierarchy.levels) for hierarchy in self._hierarchies.values()])

    def _ipython_key_completions_(self):
        return ipython_key_completions_for_mapping(self._flatten())

    def _repr_json_(self) -> ReprJson:
        # Use the dimension/hierarchy/level in the map key to make it unique.
        data = {
            f"{level.name} ({level.dimension}/{level.hierarchy}/{level.name})": level._repr_json_()[
                0
            ]
            for hierarchy in self._hierarchies.values()
            for level in hierarchy.levels.values()
        }
        sorted_data = dict(sorted(data.items(), key=operator.itemgetter(0)))
        return (
            sorted_data,
            {
                "expanded": True,
                "root": "Levels",
            },
        )
