# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Computation of AutoML model evaluation metrics."""
import logging
import numpy as np
import time

from sklearn.base import TransformerMixin
from sklearn.utils import resample
from typing import Dict, List, Optional, Tuple, Type

from azureml.automl.core.shared import logging_utilities

from azureml.automl.core.shared.constants import MetricExtrasConstants
from azureml.automl.runtime.shared.score._classification import ClassificationMetric
from azureml.automl.runtime.shared.score import _scoring_utilities, _validation, constants

logger = logging.getLogger(__name__)


def score_confidence_intervals_classification(
    y_test: np.ndarray,
    y_pred_probs: np.ndarray,
    metrics: List[str],
    class_labels: np.ndarray,
    train_labels: np.ndarray,
    sample_weight: Optional[np.ndarray] = None,
    y_transformer: Optional[TransformerMixin] = None,
    use_binary: bool = False
) -> Dict[str, Dict[str, float]]:
    """
    Compute confidence interval metrics for a classification task.

    All class labels for y should come
    as seen by the fitted model (i.e. if the fitted model uses a y transformer the labels
    should also come transformed).

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if the calculation failed.

    :param y_test: The target values (Transformed if using a y transformer)
    :param y_pred_probs: The predicted probabilities for all classes.
    :param metrics: Classification metrics to compute
    :param class_labels: All classes found in the full dataset (includes train/valid/test sets).
        These should be transformed if using a y transformer.
    :param train_labels: Classes as seen (trained on) by the trained model. These values
        should correspond to the columns of y_pred_probs in the correct order.
    :param sample_weight: Weights for the samples (Does not need
        to match sample weights on the fitted model)
    :param y_transformer: Used to inverse transform labels from `y_test`. Required for non-scalar metrics.
    :param use_binary: Compute metrics only on the true class for binary classification.
    :return: A dictionary mapping metric name to metric score.
    """

    y_test = _validation.format_1d(y_test, 'y_test')

    _validation.validate_classification(y_test, y_pred_probs, metrics,
                                        class_labels, train_labels,
                                        sample_weight, y_transformer)

    _validation.log_classification_debug(y_test, y_pred_probs, class_labels,
                                         train_labels, sample_weight=sample_weight)

    scoring_dto = _scoring_utilities.ClassificationDataDto(y_test,
                                                           y_pred_probs,
                                                           class_labels,
                                                           train_labels,
                                                           sample_weight,
                                                           y_transformer)

    results = {}
    for name in metrics:
        if name not in constants.CLASSIFICATION_SCALAR_SET:
            continue

        test_targets, pred_targets, labels = scoring_dto.get_targets(encoded=True)
        computed_metric = _generate_confidence_intervals(name,
                                                         test_targets, pred_targets, labels,
                                                         scoring_dto.y_pred_probs_padded,
                                                         scoring_dto.y_test_bin,
                                                         sample_weight, use_binary)
        if computed_metric is not None:
            results[name] = computed_metric

    return results


def _generate_confidence_intervals(
    name: str,
    test_targets: np.ndarray,
    pred_targets: np.ndarray,
    labels: np.ndarray,
    y_pred_probs_padded: np.ndarray,
    y_test_bin: np.ndarray,
    sample_weight: Optional[np.ndarray] = None,
    use_binary: bool = False,
) -> Optional[Dict[str, float]]:
    """
    Bootstrap sampling on the pre-scored dataset to create confidence intervals on
    the metrics.

    Bootstrap sampling is used on the scoring dataset to create a confidence interval
    for all scalar metrics. The dataset prediction step is done exactly once, the predictions
    are bootstrapped N-times, metrics are calculated on these N bootstrap samples, the
    2.5th/97.5th percentile of the bootstrap metrics are the returned as the lower/upper 95th
    percentile confidence intervals

    :param name: Name of the metric being computed
    :param results: Dict of metric values
    :param test_targets: The target values (Transformed if using a y transformer)
    :param pred_targets: The predicted class.
    :param labels: All classes found in the full dataset (includes train/valid/test sets).
        These should be transformed if using a y transformer.
    :param y_pred_probs_padded: the predicted classes padded
    :param y_test_bin: The actual class labels
    :param sample_weight: Weights for the samples (Does not need
        to match sample weights on the fitted model)
    :param use_binary: Compute metrics only on the true class for binary classification.
    :return: Dict of table metrics.
    """

    metric_class = _scoring_utilities.get_metric_class(name)
    safe_name = _scoring_utilities.get_safe_metric_name(name)
    start_time = time.perf_counter()

    aggregated_metrics = None
    try:
        metric_values, time_for_metric_compute, time_for_resample = _bootstrap_samples(metric_class,
                                                                                       300,
                                                                                       test_targets,
                                                                                       pred_targets,
                                                                                       labels,
                                                                                       y_pred_probs_padded,
                                                                                       y_test_bin,
                                                                                       sample_weight,
                                                                                       use_binary)

        aggregated_metrics = _calculate_confidence_intervals(metric_values)

        logger.info('Bootstrap scoring metric compution for test dataset took {:0.4f} seconds for metric "{}"'
                    .format(time_for_metric_compute, safe_name))
        logger.info('Bootstrap resample for test dataset took {:0.4f} seconds for metric "{}"'
                    .format(time_for_resample, safe_name))

    except Exception as e:
        logger.error("Bootstrap sampling failed for classification metric {}".format(safe_name))
        logging_utilities.log_traceback(e, logger, is_critical=False)

    time_for_bootstrapping = time.perf_counter() - start_time
    logger.info('Bootstrap scoring for test dataset took {:0.4f} seconds for metric "{}"'
                .format(time_for_bootstrapping, safe_name))

    return aggregated_metrics


def _bootstrap_samples(
    metric_class: Type[ClassificationMetric],
    iterations: int,
    test_targets: np.ndarray,
    pred_targets: np.ndarray,
    labels: np.ndarray,
    y_pred_probs_padded: np.ndarray,
    y_test_bin: np.ndarray,
    sample_weight: Optional[np.ndarray] = None,
    use_binary: bool = False
) -> Tuple[List[float], float, float]:

    test_targets_orig = test_targets
    pred_targets_orig = pred_targets
    y_pred_probs_padded_orig = y_pred_probs_padded
    y_test_bin_orig = y_test_bin
    pred_targets_orig = pred_targets
    sample_weight_orig = sample_weight

    time_for_metric_compute = 0.0
    time_for_resample = 0.0

    metric_values = []  # type: List[float]

    for i in range(iterations):  # Should be ~300
        # Bootstrap sample
        resample_start_time = time.perf_counter()
        if sample_weight_orig is None:
            test_targets, pred_targets, y_pred_probs_padded, y_test_bin, pred_targets = \
                resample(test_targets_orig, pred_targets_orig, y_pred_probs_padded_orig,
                         y_test_bin_orig, pred_targets_orig, random_state=i, replace=True)
        else:
            test_targets, pred_targets, y_pred_probs_padded, y_test_bin, pred_targets, sample_weight = \
                resample(test_targets_orig, pred_targets_orig, y_pred_probs_padded_orig,
                         y_test_bin_orig, pred_targets_orig, sample_weight_orig, random_state=i, replace=True)
        time_for_resample += time.perf_counter() - resample_start_time

        metric = metric_class(test_targets, y_pred_probs_padded, y_test_bin, pred_targets, labels,
                              sample_weight=sample_weight, use_binary=use_binary)

        metric_compute_start_time = time.perf_counter()
        computed_metric = metric.compute()
        time_for_metric_compute += time.perf_counter() - metric_compute_start_time
        metric_values.append(computed_metric)

    return metric_values, time_for_resample, time_for_metric_compute


def _calculate_confidence_intervals(
    metric_values: List[float],
) -> Dict[str, float]:
    """
    Compute aggregate model evaluation metrics from the bootstrap scoring

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if metric calculation failed.

    :param metrics_values:
        List containing metric values from the bootstrap metric
        calculation: [0.9, 0.8, ...]}.
    :return: Dictionary of confidence interval, etc.
    """
    metrics_extras = {}  # type: Dict[str, float]
    metrics_extras[MetricExtrasConstants.LOWER_95_PERCENTILE] = np.nanpercentile(metric_values, 2.5)
    metrics_extras[MetricExtrasConstants.UPPER_95_PERCENTILE] = np.nanpercentile(metric_values, 97.5)

    return metrics_extras
