# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict

import torch
from azureml.contrib.automl.dnn.forecasting._transforms.tensor_transforms import ComposableTransform, \
    LogTransform, SubtractOffsetTransform
from forecast.data import FUTURE_DEP_KEY, PAST_DEP_KEY


class TCNBatchTransform:
    """Transform a batch of data in a TCN network.

    This transform converts the targets to log space, then performs a subtract offset on the targets."""

    def __init__(self) -> None:
        self._transform = ComposableTransform([LogTransform(1), SubtractOffsetTransform()])

    def do(self, batch: Dict[str, torch.Tensor]):
        """Transform the batch."""
        batch = dict(batch)
        batch[PAST_DEP_KEY] = self._transform.fit_transform(batch[PAST_DEP_KEY])
        batch[FUTURE_DEP_KEY] = self._transform.transform(batch[FUTURE_DEP_KEY])
        return batch

    def undo_y(self, y: torch.Tensor) -> torch.Tensor:
        """Reverse the transformation on the predictions."""
        return self._transform.reverse_transform(y)
