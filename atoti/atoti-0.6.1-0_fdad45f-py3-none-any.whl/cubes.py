from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from typeguard import typeguard_ignore

from ._local_cubes import LocalCubes
from .cube import Cube

if TYPE_CHECKING:
    from .session import Session


@typeguard_ignore
@dataclass(frozen=True)
class Cubes(LocalCubes[Cube]):
    """Manage the cubes of the session."""

    _session: Session = field(repr=False)
