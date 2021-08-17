# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for all samplers."""
from typing import Any, Dict, Tuple

from abc import ABC, abstractmethod

from azureml.automl.core.shared import constants
from azureml.automl.runtime.shared.types import DataInputType, DataSingleColumnInputType
from . import SplittingConfig


class AbstractSampler(ABC):
    """Base class for all samplers."""

    def __init__(self,
                 task: str = constants.Tasks.CLASSIFICATION,
                 *args: Any, **kwargs: Any) -> None:
        """Initialize logger for the sub class."""
        self._task = task

    @abstractmethod
    def sample(self, X: DataInputType, y: DataSingleColumnInputType) \
            -> Tuple[DataInputType, DataSingleColumnInputType, SplittingConfig]:
        """All sub classes should implement this."""
        raise NotImplementedError()

    def __getstate__(self) -> Dict[str, Any]:
        """
        Get state picklable objects.

        :return: state
        """
        return self.__dict__

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        self.__dict__.update(state)
