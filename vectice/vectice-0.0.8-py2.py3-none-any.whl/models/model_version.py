from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .artifact import _Base
from .with_metrics import WithMetrics
from .with_properties import WithProperties
from .with_version import WithVersion


@dataclass
class ModelVersion(_Base, WithVersion, WithProperties, WithMetrics):
    algorithmName: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    """"""

    def with_algorithm(self, name: Optional[str]):
        """Accepts an optional str and sets the algorithmName.

        :param name: The model's algorithm
        """
        self.algorithmName = name

    def with_status(self, status: Optional[str]):
        """Accepts an optional str and sets the model status.

        :param status: The model's status
        """
        self.status = status

    def with_type(self, type: Optional[str]):
        """Accepts an optional str and sets the model type.

        :param type: The model's type
        """
        self.type = type
