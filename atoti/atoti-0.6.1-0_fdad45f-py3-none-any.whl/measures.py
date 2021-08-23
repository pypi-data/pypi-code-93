from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict

from typeguard import typeguard_ignore

from ._local_measures import LocalMeasures
from .exceptions import AtotiJavaException
from .measure import Measure
from .measure_description import (
    MeasureDescription,
    MeasureLike,
    _convert_to_measure_description,
)

if TYPE_CHECKING:
    from ._java_api import JavaApi
    from .cube import Cube


def _validate_name(name: str):
    """Validate the measure name.

    Args:
        name: The name to check.
    """
    if "," in name:
        raise ValueError(f'Invalid measure name "{name}". "," are not allowed.')
    if name != name.strip():
        raise ValueError(
            f'Invalid measure name "{name}". Leading or trailing whitespaces are not allowed.'
        )
    if name.startswith("__hidden_"):
        raise ValueError(
            f'Invalid measure name "{name}". Name cannot start with "__hidden_".'
        )


@dataclass(init=False)
class Measures(LocalMeasures[Measure]):
    """Manage the measures."""

    @typeguard_ignore
    def __init__(self, java_api: JavaApi, cube: Cube = field(repr=False)):
        super().__init__(java_api)
        self._cube = cube

    @typeguard_ignore
    def _build_measure(
        self, name: str, description: JavaApi.JavaMeasureDescription
    ) -> Measure:
        return Measure(
            name,
            description.underlying_type,
            self._cube,
            self._java_api,
            description.folder,
            description.formatter,
            description.visible,
            description.description,
        )

    def _get_underlying(self) -> Dict[str, Measure]:
        """Fetch the measures from the JVM each time they are needed."""
        cube_measures = self._java_api.get_full_measures(self._cube)
        return {
            name: self._build_measure(name, cube_measures[name])
            for name in cube_measures
        }

    def __getitem__(self, key: str) -> Measure:
        """Return the measure with the given name."""
        try:
            cube_measure = self._java_api.get_measure(self._cube, key)
            return self._build_measure(key, cube_measure)
        except AtotiJavaException:
            raise KeyError(f"No measure named {key}") from None

    def __setitem__(self, key: str, value: MeasureLike):
        """Publish the measure with the given name.

        If the input is not a MeasureDescription, its ``_to_measure_description`` method will be called.

        Args:
            key: The name of the measure to add.
            value: The measure to add.
        """
        _validate_name(key)

        if not isinstance(value, MeasureDescription):
            value = _convert_to_measure_description(value)

        try:
            value._distil(java_api=self._java_api, cube=self._cube, measure_name=key)
        except AttributeError as err:
            raise ValueError(f"Cannot create a measure from {value}") from err

        self._java_api.publish_measures(self._cube.name)

    def __delitem__(self, key: str):
        """Delete a measure.

        Args:
            key: The name of the measure to delete.
        """
        found = self._java_api.delete_measure(cube=self._cube, measure_name=key)
        if not found:
            raise KeyError(f"{key} is not an existing measure.")
        self._java_api.refresh()
