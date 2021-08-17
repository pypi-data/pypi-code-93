# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to a Regression task type."""

from typing import Any, Dict, List, Optional, Union

import numpy as np

from azureml.automl.runtime.shared.score import scoring


def evaluate_regressor(
        y_test: np.ndarray,
        y_pred: np.ndarray,
        metrics: List[str],
        y_max: Optional[float] = None,
        y_min: Optional[float] = None,
        y_std: Optional[float] = None,
        sample_weight: Optional[np.ndarray] = None,
        bin_info: Optional[Dict[str, float]] = None,
) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Given the scored data, generate metrics for classification task.
    The optional parameters `y_min`, `y_min`, and `y_min` should be based on the target column y from the
    full dataset.

    - `y_max` and `y_min` should be used to control the normalization of
    normalized metrics. The effect will be division by max - min.
    - `y_std` is used to estimate a sensible range for displaying non-scalar
    regression metrics.

    If the metric is undefined given the input data, the score will show
        as nan in the returned dictionary.

    :param y_test: The target values.
    :param y_pred: The predicted values.
    :param metrics: List of metric names for metrics to calculate.
    :type metrics: list
    :param y_max: The max target value.
    :param y_min: The min target value.
    :param y_std: The standard deviation of targets value.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :param bin_info:
        The binning information for true values. This should be calculated from make_dataset_bins. Required for
        calculating non-scalar metrics.
    :return: A dictionary mapping metric name to metric score.
    """
    return scoring.score_regression(y_test, y_pred, metrics, y_max, y_min, y_std, sample_weight, bin_info)
