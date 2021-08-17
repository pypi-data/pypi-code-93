# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import List, Optional

import torch
from azureml.automl.core.shared._diagnostics.contract import Contract


def _copy(x):
    return x.detach().clone()


class AbstractTensorTransform(ABC):
    """Abstract class for a transform that operates on a tensor."""

    @abstractmethod
    def fit(self, tensor: torch.Tensor) -> None:
        """Fit the transform."""
        raise NotImplementedError

    @abstractmethod
    def transform(self, tensor: torch.Tensor) -> torch.Tensor:
        """Transform a tensor."""
        raise NotImplementedError

    @abstractmethod
    def reverse_transform(self, tensor: torch.Tensor) -> torch.Tensor:
        """Reverse the transform."""
        raise NotImplementedError

    def fit_transform(self, tensor: torch.Tensor) -> torch.Tensor:
        """Fit the transform on a tensor, then transform that tensor and return the result."""
        self.fit(tensor)
        return self.transform(tensor)


class ComposableTransform(AbstractTensorTransform):
    """Transform composed of a list of sequentially-applied tensor transforms."""

    def __init__(self, tfs: List[AbstractTensorTransform]) -> None:
        self._tfs = tfs

    def fit(self, tensor):
        raise NotImplementedError

    def fit_transform(self, tensor: torch.Tensor) -> None:
        """Fit the transform."""
        for tf in self._tfs:
            tensor = tf.fit_transform(tensor)
        return tensor

    def transform(self, tensor: torch.Tensor) -> torch.Tensor:
        """Transform a tensor."""
        for tf in self._tfs:
            tensor = tf.transform(tensor)
        return tensor

    def reverse_transform(self, tensor: torch.Tensor) -> torch.Tensor:
        """Reverse the transform."""
        for tf in self._tfs[::-1]:
            tensor = tf.reverse_transform(tensor)
        return tensor


class LogTransform(AbstractTensorTransform):
    """Natural logarithm of target + `offset`."""

    def __init__(self, offset: float) -> None:
        self._offset = offset

    def fit(self, tensor: torch.Tensor) -> None:
        """Fit the transform."""
        return

    def transform(self, tensor: torch.Tensor) -> torch.Tensor:
        """Computes the natural logarithm of the target after applying an optional offset."""
        x = _copy(tensor)
        return torch.log(self._offset + x)

    def reverse_transform(self, tensor: torch.Tensor) -> torch.Tensor:
        """Undoes a previously applied natural logarithm on the targets."""
        x = _copy(tensor)
        return torch.exp(x) - self._offset


class SubtractOffsetTransform(AbstractTensorTransform):
    """For a series of target values, subtract value at the last index of the time series."""

    def __init__(self) -> None:
        self._offset: Optional[torch.Tensor] = None

    def fit(self, tensor: torch.Tensor) -> None:
        """Determine the offset."""
        x = _copy(tensor)
        self._offset = x[:, :, -1].squeeze()

    def transform(self, tensor: torch.Tensor) -> torch.Tensor:
        """For a series of target values, subtract value at the last index of the time series."""
        Contract.assert_value(
            self._offset,
            "The offset was not set for this substract transform. Likely, this transform was not fit.",
            log_safe=True)
        x = _copy(tensor)
        return (x.T - self._offset).T

    def reverse_transform(self, tensor: torch.Tensor) -> torch.Tensor:
        """For a series of targets, adds back the offset which was previously subtracted."""
        x = _copy(tensor)
        return (x.T + self._offset).T
