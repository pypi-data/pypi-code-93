from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Tuple

from typeguard import typechecked, typeguard_ignore

from ._base._base_measure import BaseMeasure
from ._bitwise_operators_only import IdentityElement
from .measure_description import MeasureDescription
from .type import DataType

if TYPE_CHECKING:
    from ._java_api import JavaApi
    from .cube import Cube


@typeguard_ignore
@dataclass(eq=False)
class Measure(MeasureDescription, BaseMeasure):
    """A measure is a mostly-numeric data value, computed on demand for aggregation purposes.

    Measures can be compared to other objects, such as a literal value, a :class:`~atoti.level.Level`, or another measure.
    The returned measure represents the outcome of the comparison and this measure can be used as a condition.
    If the measure's value is ``None`` when evaluating a condition, the returned value will be ``False``.

    Example:
        >>> df = pd.DataFrame(
        ...     columns=["Id", "Value", "Threshold"],
        ...     data=[
        ...         (0, 1.0, 5.0),
        ...         (1, 2.0, None),
        ...         (2, 3.0, 3.0),
        ...         (3, 4.0, None),
        ...         (4, 5.0, 1.0),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys=["Id"], table_name="Measure example")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> m["Condition"] = m["Value.SUM"] > m["Threshold.SUM"]
        >>> cube.query(m["Condition"], levels=[l["Id"]])
           Condition
        Id
        0      False
        1      False
        2      False
        3      False
        4       True

    """

    _name: str
    _data_type: DataType
    _cube: Cube = field(repr=False)
    _java_api: JavaApi = field(repr=False)
    _folder: Optional[str] = None
    _formatter: Optional[str] = None
    _visible: bool = True
    _description: Optional[str] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def folder(self) -> Optional[str]:
        """Folder of the measure.

        It can be changed by assigning a new value to the property (``None`` to clear it).
        """
        return self._folder

    @property
    def data_type(self) -> DataType:
        """Type of the measure members."""
        return self._data_type

    @folder.setter
    @typechecked
    def folder(self, value: Optional[str]):
        """Folder setter."""
        self._folder = value
        self._java_api.set_measure_folder(
            cube_name=self._cube.name, measure=self, folder=value
        )
        self._java_api.publish_measures(self._cube.name)

    @property
    def formatter(self) -> Optional[str]:
        """Formatter of the measure.

        It can be changed by assigning a new value to the property (``None`` to clear it).

        Examples:
            * ``DOUBLE[0.00%]`` for percentages
            * ``DOUBLE[#,###]`` to remove decimals
            * ``DOUBLE[$#,##0.00]`` for dollars
            * ``DATE[yyyy-MM-dd HH:mm:ss]`` for datetimes

        The spec for the pattern between the ``DATE`` or ``DOUBLE``'s brackets is the one from `Microsoft Analysis Services <https://docs.microsoft.com/en-us/analysis-services/multidimensional-models/mdx/mdx-cell-properties-format-string-contents?view=asallproducts-allversions>`__.
        The formatter only impacts how the measure is displayed, derived measures will still be computed from unformatted value.
        To round a measure, use :func:`atoti.math.round` instead.

        atoti provides an extra formatter for array measures: ``ARRAY['|';1:3]`` where ``|`` is the separator used to join the elements of the ``1:3`` slice.
        """
        return self._formatter

    @formatter.setter
    @typechecked
    def formatter(self, value: Optional[str]):
        """Formatter setter."""
        self._formatter = value
        self._java_api.set_measure_formatter(
            cube_name=self._cube.name, measure=self, formatter=value
        )
        self._java_api.publish_measures(self._cube.name)

    @property
    def visible(self) -> bool:
        """Whether the measure is visible or not.

        It can be toggled by assigning a new boolean value to the property.
        """
        return self._visible

    @visible.setter
    @typechecked
    def visible(self, value: bool):
        """Visibility setter."""
        self._visible = value
        self._java_api.set_visible(
            cube_name=self._cube.name, measure=self, visible=value
        )
        self._java_api.publish_measures(self._cube.name)

    @property
    def description(self) -> Optional[str]:
        """Description of the measure."""
        return self._description

    @description.setter
    @typechecked
    def description(self, value: Optional[str]):
        """Set the description of the measure."""
        self._description = value
        self._java_api.set_measure_description(
            cube_name=self._cube.name, measure=self, description=value
        )
        self._java_api.publish_measures(self._cube.name)

    @property
    def _required_levels(self) -> List[str]:
        """Levels required by this measure."""
        return self._java_api.get_required_levels(self)

    def _do_distil(  # pylint: disable=no-self-use
        self, *, java_api: JavaApi, cube: Cube, measure_name: Optional[str] = None
    ) -> str:
        raise ValueError("Cannot create a measure that already exists in the cube.")

    def _identity(self) -> Tuple[IdentityElement, ...]:
        return (self._name,)
