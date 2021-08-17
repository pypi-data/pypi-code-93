# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for calculating metrices for forecast dnn training."""
import logging
import math
import numpy as np
from typing import Dict, Any, Union

import azureml.automl.core   # noqa: F401
from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import DataException, ValidationException

from azureml.automl.runtime.shared import metrics as classical_metrics
from azureml.automl.runtime.shared import _dataset_binning

from azureml.automl.core.shared import logging_utilities
from azureml.automl.runtime._metrics_logging import log_metrics
from ..constants import ForecastConstant
import Deep4Cast.deep4cast.metrics as forecast_metrics
from forecast.data import FUTURE_DEP_KEY


def _get_worst_scores(metric_names):
    epslon = 0.00001
    worst_scores = classical_metrics.get_worst_values(task=constants.Tasks.REGRESSION)
    metric_objectives = classical_metrics.get_default_metric_with_objective(task=constants.Tasks.REGRESSION)
    scores = {}
    for name in metric_names:
        if name in worst_scores:
            scores[name] = worst_scores[name]
            # Update the values to avoid the assert for worst values.
            if name in metric_objectives:
                if metric_objectives[name] == constants.OptimizerObjectives.MAXIMIZE:
                    scores[name] -= epslon
                else:
                    scores[name] += epslon
    return scores


def compute_metric(y_pred, y_true_forecast, horizon, scalar_only=True, logger: logging.Logger = None) \
        -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute the classic and time series metric for the training.

    :param y_pred: forecasted target values.
    :param y_true_forecast: actual target values.
    :param horizon: horizon used for predictions.
    :param scalar_only: whether to compute scalar metrices only.
    :param logger: the logger to report all errors.
    :return: scores dictionary.
    """
    y_true_classical = y_true_forecast.reshape(-1)
    y_pred_classical = y_pred.reshape(-1)
    bin_info = None
    metrics_to_compute = constants.Metric.SCALAR_REGRESSION_SET
    worst_scores = _get_worst_scores(metrics_to_compute)
    computed_scores = {}
    try:
        if not scalar_only:
            bin_info = _dataset_binning.make_dataset_bins(y_true_classical.shape[0], y_true_classical)
            metrics_to_compute = constants.Metric.REGRESSION_SET

        computed_scores = classical_metrics.compute_metrics(y_pred_classical, y_true_classical,
                                                            task=constants.Tasks.REGRESSION,
                                                            metrics=metrics_to_compute,
                                                            bin_info=bin_info)

        # reshape prediction
        # Number of samples predicted per item based on the distribution
        number_of_samples_per_prediction = y_pred.shape[0]
        # Number of forecasting series to predict.
        number_of_items_to_predict = y_true_forecast.shape[0]
        # Number of target variables, we only support one dimensional y.
        number_of_target_variables = 1
        time_steps = horizon
        y_pred = y_pred.reshape(number_of_samples_per_prediction,
                                number_of_items_to_predict,
                                number_of_target_variables,
                                time_steps)
        computed_scores[constants.Metric.ForecastMAPE] = forecast_metrics.mape(y_pred, y_true_forecast).mean()

    except (ValueError, DataException, ValidationException) as e:
        if logger is not None:
            logging_utilities.log_traceback(e, logger)

    for name in worst_scores:
        # if metric not in computed metrics, i.e an exception, the set the metric to be worst
        # if the metric is nan then replace it with worst score.
        if name not in computed_scores or math.isnan(computed_scores[name]):
            computed_scores[name] = worst_scores[name]
    return computed_scores


def get_target_values(model, ds_test):
    """Get target y values in dataloader indexed order."""
    ds_test._keep_untransformed = True
    y_true_forecast = []
    batch_size = model.params.get_value(ForecastConstant.Batch_size)
    dataloader = model.create_data_loader(ds_test, batch_size)
    for i, batch in enumerate(dataloader):
        if ds_test.has_past_regressors:
            y_true_forecast.append(batch[FUTURE_DEP_KEY].numpy())
        else:
            y_true_forecast.append(batch["y"].numpy())
    y_true_forecast = np.concatenate(y_true_forecast, axis=0)
    ds_test._keep_untransformed = False
    return y_true_forecast


def _undo_transform(model, sample):
    sample = model._transform.undo(sample)
    return sample


def save_metric(run, scores):
    """
    Save the metrics into the run history/artifact store.

    :param run: azureml run context
    :param scores: dictionary of score name and values.
    :return: None
    """
    log_metrics(run, scores)
