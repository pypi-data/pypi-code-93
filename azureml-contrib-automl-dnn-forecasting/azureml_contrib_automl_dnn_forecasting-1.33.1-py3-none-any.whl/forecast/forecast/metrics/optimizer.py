"""Metrics related to the status of the optimizer."""
from typing import Mapping, Sequence

import numpy as np
from torch.optim.lr_scheduler import _LRScheduler

from forecast.metrics import Metric, MetricMode


class LearningRate(Metric):
    """Adds the current learning rate to the metrics passed to callbacks."""

    def __init__(self, sched: _LRScheduler, group_index: int = 0):
        """Adds the current learning rate of parameter group `index` to the metrics passed to callbacks."""
        super().__init__(MetricMode.TRAIN)
        self._sched = sched
        self._index = group_index

    def update_state(self, inputs: Mapping[str, np.ndarray], act: np.ndarray, pred: Sequence[np.ndarray]) -> None:
        """No op."""
        pass

    def reset_state(self) -> None:
        """No op."""
        pass

    def result(self) -> float:
        """Returns the current learning rate.

        Returns
        -------
        float

        """
        return self._sched.get_lr()[self._index]
