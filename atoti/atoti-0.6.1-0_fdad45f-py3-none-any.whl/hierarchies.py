from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Mapping, Sequence, Tuple, Union

from typeguard import typechecked, typeguard_ignore

from ._base._base_hierarchies import _HierarchyKey
from ._local_hierarchies import LocalHierarchies
from .hierarchy import Hierarchy
from .level import Level
from .table import Column
from .type import DataType

if TYPE_CHECKING:
    from .cube import Cube

LevelOrColumn = Union[Level, Column]


@typeguard_ignore
@dataclass(frozen=True)
class Hierarchies(LocalHierarchies[Hierarchy]):
    """Manage the hierarchies.

    A hierarchy can be renamed by creating a new one with the same levels and then removing the old one.

    Example:
        >>> prices_df = pd.DataFrame(
        ...     columns=["Nation", "City", "Price"],
        ...     data=[
        ...         ("France", "Paris", 20.0),
        ...         ("France", "Lyon", 15.0),
        ...         ("France", "Toulouse", 10.0),
        ...         ("UK", "London", 20.0),
        ...         ("UK", "Manchester", 15.0),
        ...     ],
        ... )
        >>> table = session.read_pandas(prices_df, table_name="Prices")
        >>> cube = session.create_cube(table)
        >>> h = cube.hierarchies
        >>> h["Country"] = h["Nation"].levels
        >>> del h["Nation"]
    """

    _cube: Cube = field(repr=False)

    def _get_underlying(self) -> Mapping[Tuple[str, str], Hierarchy]:
        return self._retrieve_hierarchies(self._java_api, self._cube)

    @typechecked
    def __getitem__(self, key: _HierarchyKey) -> Hierarchy:
        (dimension_name, hierarchy_name) = self._convert_key(key)
        hierarchies = self._java_api.retrieve_hierarchy(
            hierarchy_name,
            cube=self._cube,
            dimension=dimension_name,
        )
        if len(hierarchies) == 0:
            raise KeyError(f"Unknown hierarchy: {key}")
        if len(hierarchies) == 1:
            return hierarchies[0]
        raise self._multiple_hierarchies_error(key, hierarchies)

    @typechecked
    def __setitem__(
        self,
        key: _HierarchyKey,
        value: Union[Sequence[LevelOrColumn], Mapping[str, LevelOrColumn]],
    ):
        (dimension_name, hierarchy_name) = self._convert_key(key)
        if isinstance(value, Sequence):
            value = {column.name: column for column in value}
        elif not isinstance(value, Mapping):
            raise ValueError(
                f"Levels argument is expected to be a sequence or a mapping but is "
                f"{str(type(value).__name__)}"
            )
        # convert to Level
        levels: Mapping[str, Level] = {
            levelName: levelOrColumn
            if isinstance(levelOrColumn, Level)
            else Level(
                levelName,
                levelOrColumn.name,
                DataType(java_type="Object", nullable=True),
            )
            for (levelName, levelOrColumn) in value.items()
        }

        # If the hierarchy is a single level hierarchy created from a table field, we
        # automatically put it in a dimension with the same name as the table
        # If the hierarchy is multilevel, the dimension is that of the table of the top most
        # level of the hierarchy.
        if dimension_name is None:
            first_item = list(value.values())[0]
            if isinstance(first_item, Level):
                dimension_name = first_item.dimension
            else:
                dimension_name = first_item._table.name

        hierarchies = self._java_api.retrieve_hierarchy(
            hierarchy_name,
            cube=self._cube,
            dimension=dimension_name,
        )
        if len(hierarchies) == 1:
            # Edit the existing hierarchy if there is one
            hierarchies[0].levels = levels
        elif len(hierarchies) == 0:
            # Create the new hierarchy
            self._java_api.create_or_update_hierarchy(
                hierarchy_name,
                cube=self._cube,
                dimension=dimension_name,
                levels=levels,
            )
            self._java_api.refresh()
        else:
            raise self._multiple_hierarchies_error(key, hierarchies)

    @typechecked
    def __delitem__(self, key: _HierarchyKey):
        try:
            self._java_api.drop_hierarchy(self._cube, self[key])
            self._java_api.refresh()
        except KeyError:
            raise KeyError(f"{key} is not an existing hierarchy.") from None
