from __future__ import annotations

from enum import IntEnum
from pydantic import BaseModel
from math import inf
from typing import Tuple, Callable, Any, TYPE_CHECKING

from attr import Attribute, attrs, attrib, evolve
from attr.validators import instance_of

if TYPE_CHECKING:
    _Validator = Callable[[Any, Attribute[Any], Any], None]


def _in_range(lower: float, upper: float, *, endpoints: bool = True) -> _Validator:
    def _range_validator_nonstrict(_: Any, attr: Attribute[Any], value: Any) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError(f"{attr.name} must be of type int or float")

        if not lower <= value <= upper:
            raise ValueError(f"{attr.name} must be between [{lower}, {upper}], recieved: {value}")

    def _range_validator_strict(_: Any, attr: Attribute[Any], value: Any) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError(f"{attr.name} must be of type int or float")

        if not lower < value < upper:
            raise ValueError(f"{attr.name} must be between ({lower}, {upper}), recieved: {value}")

    if endpoints:
        return _range_validator_nonstrict
    else:
        return _range_validator_strict


def _greater_than(lower: float, *, strict: bool = False) -> _Validator:
    return _in_range(lower, inf, endpoints=(not strict))


class Rect(BaseModel):
    x_min: float
    x_max: float
    y_min: float
    y_max: float

class ArduStackConfig(BaseModel):
    base_string: str = "tcp:127.0.0.1"
    connection_string: str = "tcp:127.0.0.1:5760"
    verbose: bool = True
    simulation_speedup: int = 1
    retries: int = 10
    use_dronekit_sitl: bool = False
    waypoint_distance_threshold: int = 10
    retry_working_dir: str = None

@attrs(auto_attribs=True, frozen=True)
class Coordinate:
    lat: float = attrib(validator=_in_range(-90, 90))
    lon: float = attrib(validator=_in_range(-180, 180))


@attrs(auto_attribs=True, frozen=True)
class Waypoint(Coordinate):
    alt: float = attrib(5.0, validator=_greater_than(0, strict=True))



class FenceType(IntEnum):
    """Enumeration of the different geofence types.

    An inclusive fence creates a boundary that the PX4 may not exit. An exclusive fence creates a boundary the PX4
    may not enter.
    """
    INCLUSIVE = 1
    EXCLUSIVE = 2


@attrs(auto_attribs=True, frozen=True)
class Geofence:
    vertices: Tuple[Coordinate, ...] = attrib(factory=tuple, converter=tuple)
    fence_type: FenceType = attrib(FenceType.EXCLUSIVE, validator=instance_of(FenceType))

    def add_vertex(self, vertex: Coordinate) -> Geofence:
        return evolve(self, vertices=self.vertices + (vertex,))


@attrs(auto_attribs=True, frozen=True)
class Mission:
    waypoints: Tuple[Waypoint, ...] = attrib(factory=tuple, converter=tuple)
    geofences: Tuple[Geofence, ...] = attrib(factory=tuple, converter=tuple)
    acceptance_radius: float = attrib(10.0, validator=_greater_than(3))

    def add_waypoint(self, waypoint: Waypoint) -> Mission:
        return evolve(self, waypoints=self.waypoints + (waypoint,))

    def remove_waypoint(self, index: int) -> Mission:
        if index < 0 or index >= len(self.waypoints):
            raise ValueError(f"Index {index} is out of bounds for waypoints")

        waypoints = (waypoint for i, waypoint in enumerate(self.waypoints) if i != index)
        return evolve(self, waypoints=waypoints)

    def add_geofence(self, geofence: Geofence) -> Mission:
        return evolve(self, geofences=self.geofences + (geofence,))

    def remove_geofence(self, index: int) -> Mission:
        if index < 0 or index >= len(self.geofences):
            raise ValueError(f"Index {index} is out of bounds for geofences")

        geofences = (geofence for i, geofence in enumerate(self.geofences) if i != index)
        return evolve(self, geofences=geofences)

    @property
    def empty(self) -> bool:
        return len(self.waypoints) == 0

