# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Definitions for forecasting metrics."""
import logging
import numpy as np

from abc import abstractmethod
from collections import OrderedDict
from typing import cast, Any, Dict, List, Optional

from azureml.automl.runtime.shared.score import _scoring_utilities, constants, _regression
from azureml.automl.runtime.shared.score._metric_base import Metric, NonScalarMetric
from azureml.automl.core.shared.exceptions import DataErrorException


_logger = logging.getLogger(__name__)


class ForecastingMetric(Metric):
    """Abstract class for forecast metrics."""

    y_pred_str = 'y_pred'
    y_test_str = 'y_test'

    def __init__(self,
                 y_test: np.ndarray,
                 y_pred: np.ndarray,
                 horizons: np.ndarray,
                 y_min: Optional[float] = None,
                 y_max: Optional[float] = None,
                 y_std: Optional[float] = None,
                 bin_info: Optional[Dict[str, float]] = None,
                 sample_weight: Optional[np.ndarray] = None) -> None:
        """
        Initialize the forecasting metric class.

        :param y_test: True labels for the test set.
        :param y_pred: Predictions for each sample.
        :param horizons: The integer horizon alligned to each y_test. These values should be computed
            by the timeseries transformer. If the timeseries transformer does not compute a horizon,
            ensure all values are the same (ie. every y_test should be horizon 1.)
        :param y_min: Minimum target value.
        :param y_max: Maximum target value.
        :param y_std: Standard deviation of the targets.
        :param bin_info: Metadata about the dataset (required for nonscalar metrics).
        :param sample_weight: Weighting of each sample in the calculation.
        """
        if y_test.shape[0] != y_pred.shape[0]:
            raise DataErrorException(
                "Mismatched input shapes: y_test={}, y_pred={}".format(y_test.shape, y_pred.shape),
                target="y_pred", reference_code="_forecasting.ForecastingMetric.__init__",
                has_pii=True).with_generic_msg("Mismatched input shapes: y_test, y_pred")
        self._y_test = y_test
        self._y_pred = y_pred
        self._horizons = horizons
        self._y_min = y_min
        self._y_max = y_max
        self._y_std = y_std
        self._bin_info = bin_info
        self._sample_weight = sample_weight

        super().__init__()

    @abstractmethod
    def compute(self) -> Dict[str, Any]:
        """Compute the score for the metric."""
        ...

    def _group_raw_by_horizon(self) -> Dict[int, Dict[str, List[float]]]:
        """
        Group y_true and y_pred by horizon.

        :return: A dictionary of horizon to y_true, y_pred.
        """
        grouped_values = {}         # type: Dict[int, Dict[str, List[float]]]
        for idx, h in enumerate(self._horizons):
            if h in grouped_values:
                grouped_values[h][ForecastingMetric.y_pred_str].append(self._y_pred[idx])
                grouped_values[h][ForecastingMetric.y_test_str].append(self._y_test[idx])
            else:
                grouped_values[h] = {
                    ForecastingMetric.y_pred_str: [self._y_pred[idx]],
                    ForecastingMetric.y_test_str: [self._y_test[idx]]
                }

        return grouped_values

    @staticmethod
    def _group_scores_by_horizon(score_data: List[Dict[int, Dict[str, Any]]]) -> Dict[int, List[Any]]:
        """
        Group computed scores by horizon.

        :param score_data: The dictionary of data from a cross-validated model.
        :return: The data grouped by horizon in sorted order.
        """
        grouped_data = {}       # type: Dict[int, List[Any]]
        for cv_fold in score_data:
            for horizon in cv_fold.keys():
                if horizon in grouped_data.keys():
                    grouped_data[horizon].append(cv_fold[horizon])
                else:
                    grouped_data[horizon] = [cv_fold[horizon]]

        # sort data by horizon
        grouped_data_sorted = OrderedDict(sorted(grouped_data.items()))
        return grouped_data_sorted


class ForecastMAPE(ForecastingMetric, NonScalarMetric):
    """Mape Metric based on horizons."""

    SCHEMA_TYPE = constants.SCHEMA_TYPE_MAPE
    SCHEMA_VERSION = '1.0.0'

    MAPE = 'mape'
    COUNT = 'count'

    def compute(self) -> Dict[str, Any]:
        """Compute mape by horizon."""
        grouped_values = self._group_raw_by_horizon()
        for h in grouped_values:
            partial_pred = np.array(grouped_values[h][ForecastingMetric.y_pred_str])
            partial_test = np.array(grouped_values[h][ForecastingMetric.y_test_str])

            self._data[h] = {
                ForecastMAPE.MAPE: _regression._mape(partial_test, partial_pred),
                ForecastMAPE.COUNT: len(partial_pred)
            }

        ret = NonScalarMetric._data_to_dict(
            ForecastMAPE.SCHEMA_TYPE,
            ForecastMAPE.SCHEMA_VERSION,
            self._data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))

    @staticmethod
    def aggregate(
        scores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fold several scores from a computed metric together.

        :param scores: List of computed scores.
        :return: Aggregated score.
        """
        if not Metric.check_aggregate_scores(scores, constants.FORECASTING_MAPE):
            return NonScalarMetric.get_error_metric()

        score_data = [score[NonScalarMetric.DATA] for score in scores]
        grouped_data = ForecastingMetric._group_scores_by_horizon(score_data)

        data = {}
        for horizon in grouped_data:
            agg_count = 0
            agg_mape = 0.0
            folds = grouped_data[horizon]
            for fold in folds:
                fold_count = fold[ForecastMAPE.COUNT]
                agg_count += fold_count
                agg_mape += fold[ForecastMAPE.MAPE] * fold_count
            agg_mape = agg_mape / agg_count
            data[horizon] = {
                ForecastMAPE.MAPE: agg_mape,
                ForecastMAPE.COUNT: agg_count
            }

        ret = NonScalarMetric._data_to_dict(
            ForecastMAPE.SCHEMA_TYPE,
            ForecastMAPE.SCHEMA_VERSION,
            data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))


class ForecastResiduals(ForecastingMetric, NonScalarMetric):
    """Forecasting residuals metric."""

    SCHEMA_TYPE = constants.SCHEMA_TYPE_RESIDUALS
    SCHEMA_VERSION = '1.0.0'

    EDGES = 'bin_edges'
    COUNTS = 'bin_counts'
    MEAN = 'mean'
    STDDEV = 'stddev'
    RES_COUNT = 'res_count'

    def compute(self) -> Dict[str, Any]:
        """Compute the score for the metric."""
        if self._y_std is None:
            raise DataErrorException(
                "y_std required to compute Residuals",
                target="_y_std", reference_code="_forecasting.ForecastResiduals.compute",
                has_pii=False)

        num_bins = 10
        # If full dataset targets are all zero we still need a bin
        y_std = self._y_std if self._y_std != 0 else 1

        self._data = {}
        grouped_values = self._group_raw_by_horizon()
        for h in grouped_values:
            self._data[h] = {}
            partial_residuals = np.array(grouped_values[h][ForecastingMetric.y_pred_str]) \
                - np.array(grouped_values[h][ForecastingMetric.y_test_str])
            mean = np.mean(partial_residuals)
            stddev = np.std(partial_residuals)
            res_count = len(partial_residuals)

            counts, edges = _regression.Residuals._hist_by_bound(partial_residuals, 2 * y_std, num_bins)
            _regression.Residuals._simplify_edges(partial_residuals, edges)
            self._data[h][ForecastResiduals.EDGES] = edges
            self._data[h][ForecastResiduals.COUNTS] = counts
            self._data[h][ForecastResiduals.MEAN] = mean
            self._data[h][ForecastResiduals.STDDEV] = stddev
            self._data[h][ForecastResiduals.RES_COUNT] = res_count

        ret = NonScalarMetric._data_to_dict(
            ForecastResiduals.SCHEMA_TYPE,
            ForecastResiduals.SCHEMA_VERSION,
            self._data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))

    @staticmethod
    def aggregate(
        scores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fold several scores from a computed metric together.

        :param scores: List of computed scores.
        :return: Aggregated score.
        """
        if not Metric.check_aggregate_scores(scores, constants.FORECASTING_RESIDUALS):
            return NonScalarMetric.get_error_metric()

        score_data = [score[NonScalarMetric.DATA] for score in scores]
        grouped_data = ForecastingMetric._group_scores_by_horizon(score_data)

        data = {}
        for horizon in grouped_data:
            # convert data to how residuals expects
            partial_scores = [{NonScalarMetric.DATA: fold_data} for fold_data in grouped_data[horizon]]
            # use aggregate from residuals
            data[horizon] = _regression.Residuals.aggregate(partial_scores)[NonScalarMetric.DATA]

        ret = NonScalarMetric._data_to_dict(
            ForecastResiduals.SCHEMA_TYPE,
            ForecastResiduals.SCHEMA_VERSION,
            data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))
