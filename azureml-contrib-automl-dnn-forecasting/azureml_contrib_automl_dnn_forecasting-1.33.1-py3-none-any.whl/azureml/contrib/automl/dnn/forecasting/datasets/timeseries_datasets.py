# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating training dataset from dapaprep Dataflow object."""
import math
from typing import Any, List, Optional, Union

import forecast.data.transforms as tfs
import numpy as np
import pandas as pd
import torch
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty, NotReady

from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY
from forecast.data.sources.data_source import DataSourceConfig
from forecast.data.sources.data_source import EncodingSpec
from torch.utils.data import Dataset

from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TimeseriesNothingToPredict, \
    ForecastHorizonExceeded
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import ConfigException, DataException, ValidationException
from azureml.automl.runtime.shared import _dataset_binning as binning
from azureml.automl.runtime import _ml_engine as ml_engine
from azureml.automl.runtime.column_purpose_detection import ColumnPurposeDetector
import azureml.automl.runtime.featurizer.transformer.timeseries as automl_transformer

from ..constants import FeatureType, ForecastConstant, DROP_COLUMN_LIST, TCNForecastParameters
from ..types import DataInputType, TargetInputType


class GrainColumnInfo:
    """This class holds a name, index and unique number of items in the column."""

    def __init__(self,
                 name: str,
                 index: int,
                 distinct_values: int):
        """
        Create a structure with grain name, index in the transformed dataset and count of distinct grain values.

        :param name: Name of a column in the timeseries grain.
        :param index: Index of the grain column in the transformed data.
        :param distinct_values: Number of distinct values in the grain column.
        """
        self.name = name
        self.index = index
        self.distinct_values = distinct_values


class _DataGrainItem:
    """This class holds a slice of feature and label."""

    def __init__(self,
                 X_df: pd.DataFrame,
                 y: np.ndarray,
                 lookup_start_ix: int = 0,
                 lookup_end_ix: int = None,
                 offset: int = 0):
        self.X_df = X_df
        self.y = y
        self.lookup_start_ix = lookup_start_ix
        self.lookup_end_ix = lookup_end_ix
        self.offset = offset

        Contract.assert_true(self.X.shape[0] == self.y.shape[-1],
                             "X({}) and y({}) have inconsistent shapes.".format(X_df.shape[0], y.shape[-1]),
                             log_safe=True)

        if lookup_end_ix:
            Contract.assert_true(self.lookup_end_ix > self.lookup_start_ix,
                                 "lookup_end_ix ({}) should be greater than lookup_start_ix ({})".format(
                                     lookup_end_ix, lookup_start_ix), log_safe=True)

    @property
    def X(self):
        """Get the numeric array of data frame needed for training sample."""
        return self.X_df.values


# Copied here temporarily, it will be imported from automl.client.core.runner.model_wrappers.
class ForecastingErrors:
    """Forecasting errors."""

    # Constants for errors and warnings
    # Non recoverable errors.
    FATAL_WRONG_DESTINATION_TYPE = ("The forecast_destination argument has wrong type, "
                                    "it is a {}. We expected a datetime.")
    FATAL_DATA_SIZE_MISMATCH = "The length of y_pred is different from the X_pred"
    FATAL_WRONG_X_TYPE = ("X_pred has unsupported type, x should be pandas.DataFrame, "
                          "but it is a {}.")
    FATAL_WRONG_Y_TYPE = ("y_pred has unsupported type, y should be numpy.array or pandas.DataFrame, "
                          "but it is a {}.")
    FATAL_NO_DATA_CONTEXT = ("No y values were provided for one of grains. "
                             "We expected non-null target values as prediction context because there "
                             "is a gap between train and test and the forecaster "
                             "depends on previous values of target. ")
    FATAL_NO_DESTINATION_OR_X_PRED = ("Input prediction data X_pred and forecast_destination are both None. "
                                      "Please provide either X_pred or a forecast_destination date, but not both.")
    FATAL_DESTINATION_AND_X_PRED = ("Input prediction data X_pred and forecast_destination are both set. "
                                    "Please provide either X_pred or a forecast_destination date, but not both.")
    FATAL_X_Y_XOR = "X_pred and y_pred should both be None or both not None."
    FATAL_NO_LAST_DATE = ("The last training date was not provided."
                          "One of grains in scoring set was not present in training set.")
    FATAL_EARLY_DESTINATION = ("Input prediction data X_pred or input forecast_destination contains dates "
                               "prior to the latest date in the training data. "
                               "Please remove prediction rows with datetimes in the training date range "
                               "or adjust the forecast_destination date.")
    FATAL_NO_TARGET_IN_Y_DF = ("The y_pred is a data frame, "
                               "but it does not contain the target value column")
    FATAL_WRONG_QUANTILE = "Quantile should be a number between 0 and 1 (not inclusive)."
    FATAL_NO_TS_TRANSFORM = ("The time series transform is absent. "
                             "Please try training model again.")

    FATAL_NO_GRAIN_IN_TRAIN = ("One of grains was not present in the training data set. "
                               "Please remove it from the prediction data set to proceed.")
    FATAL_NO_TARGET_IMPUTER = 'No target imputers were found in TimeSeriesTransformer.'
    FATAL_NONPOSITIVE_HORIZON = "Forecast horizon must be a positive integer."


class AbstractDNNTimeSeriesDataset(Dataset):
    """This abstract class provides a base class for Time Series datasets."""

    @staticmethod
    def _drop_extra_columns(X: pd.DataFrame) -> pd.DataFrame:
        drop_columns = []
        for col in X.columns:
            if col in DROP_COLUMN_LIST:
                drop_columns.append(col)
        if drop_columns:
            return X.drop(drop_columns, inplace=False, axis=1)
        return X

    def __init__(self,
                 horizon: int,
                 lookback: int,
                 step: int = 1,
                 thinning: float = 1.0,
                 has_past_regressors: bool = False,
                 pre_transform: automl_transformer.TimeSeriesTransformer = None,
                 sample_transform: Any = None,
                 fetch_y_only: bool = False,
                 training_data: tuple = None,
                 dset_config: DataSourceConfig = None,
                 data_grains: List[_DataGrainItem] = None,
                 grain_col_info: List[GrainColumnInfo] = None,
                 min_grain_for_embedding: int = TCNForecastParameters.MIN_GRAIN_SIZE_FOR_EMBEDDING_DEFAULT,
                 ):
        """
        Take a training data(X) and label(y) and provides access to windowed subseries for torch DNN training.

        :param horizon: Number of time steps to forecast.
        :param lookback: lookback for this class.
        :param step: Time step size between consecutive examples.
        :param thinning: Fraction of examples to include.
        :param has_past_regressors: data to populate past regressors for each sample
        :param pre_transform: pre_transformer to use
        :param sample_transform: per-sample feature transforms to use
        :param fetch_y_only: Get only the target value.
        :param train_transform: whether training is needed for transformers
        :param training_data: X and Y and settings saved in dataset if needed to created lookback.
        :param dset_config: Get only the target value.
        :param data_grain: Slices of data grain and the indexes to lookup the training sample.
        :param grain_col_info: List of grain columns index, count and name.
        :param min_grain_for_embedding: min number of grains to enable embedding.
        """
        self.horizon = horizon
        self.step = step
        self.thinning = thinning
        self.sample_transform = sample_transform
        self._pre_transform = pre_transform
        self._keep_untransformed = False
        self.has_past_regressors = has_past_regressors
        self._len = None
        self.lookback = lookback
        self.fetch_y_only = fetch_y_only
        self._training_data = training_data
        self.dset_config = dset_config
        self._cache = {}
        self._data_grains = data_grains
        self._grain_col_info = grain_col_info
        if self._pre_transform is not None:
            Contract.assert_type(self._pre_transform, "pre_transform", automl_transformer.TimeSeriesTransformer)
        self.cross_validation = None
        self._min_grain_for_embedding = min_grain_for_embedding
        # The `forecast` submodule / library requires this property to be set
        self.transform = None
        if not isinstance(min_grain_for_embedding, int):
            raise ValidationException('min_grain_for_embedding is not int')

    @property
    def keep_untransformed(self):
        """Whether to return data untransformed."""
        return self._keep_untransformed

    @property
    def pre_transform(self):
        """Pre transforms for this timeseries dataset."""
        return self._pre_transform


class TimeSeriesDataset(AbstractDNNTimeSeriesDataset):
    """This class provides a dataset for training timeseries model with dataprep features and label."""

    def __init__(self,
                 X_dflow: DataInputType,
                 y_dflow: TargetInputType,
                 horizon: int,
                 step: int = 1,
                 thinning: float = 1.0,
                 has_past_regressors: bool = False,
                 one_hot: bool = False,
                 pre_transform: automl_transformer.TimeSeriesTransformer = None,
                 sample_transform: Any = None,
                 train_transform: bool = False,
                 fetch_y_only: bool = False,
                 save_last_lookback_data: bool = False,
                 min_grain_for_embedding: int = TCNForecastParameters.MIN_GRAIN_SIZE_FOR_EMBEDDING_DEFAULT,
                 **settings: Any,
                 ):
        """
        Take a training data(X) and label(y) and provides access to windowed subseries for torch DNN training.

        :param X_dflow: Training features in DataPrep DataFlow form(numeric data of shape(row_count, feature_count).
        :param y_dflow: Training label in DataPrep DataFlow for with shape(row_count, 1).
        :param horizon: Number of time steps to forecast.
        :param step: Time step size between consecutive examples.
        :param thinning: Fraction of examples to include.
        :param has_past_regressors: data to populate past regressors for each sample
        :param one_hot: one_hot encode or not
        :param pre_transform: pre_transformer to use
        :param sample_transform: feature transforms to use
        :param train_transform: whether training is needed for transformers
        :param settings: automl timeseries settings for pre_transform
        """
        AbstractDNNTimeSeriesDataset.__init__(self,
                                              horizon,
                                              None,
                                              step=step,
                                              thinning=thinning,
                                              has_past_regressors=has_past_regressors,
                                              pre_transform=pre_transform,
                                              sample_transform=sample_transform,
                                              fetch_y_only=fetch_y_only,
                                              min_grain_for_embedding=min_grain_for_embedding
                                              )
        if self._pre_transform is not None:
            assert isinstance(self._pre_transform, automl_transformer.TimeSeriesTransformer)
        if isinstance(X_dflow, pd.DataFrame):
            X_df = X_dflow
        else:
            X_df = X_dflow.to_pandas_dataframe(extended_types=True)

        if isinstance(y_dflow, np.ndarray) or isinstance(y_dflow, pd.Series):
            y_df = pd.DataFrame(y_dflow)
        elif isinstance(y_dflow, pd.DataFrame):
            y_df = y_dflow
        else:
            y_df = y_dflow.to_pandas_dataframe(extended_types=True)

        # set the grain_column_names if there is no grain column.
        if ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES not in settings:
            settings[ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES] = None

        if save_last_lookback_data:
            self._training_data = (X_df, y_df, settings)

        if isinstance(horizon, str):
            settings[ForecastConstant.Horizon] = ForecastConstant.auto
        get_encodings, encodings = False, []
        if ForecastConstant.cross_validations in settings and settings[ForecastConstant.cross_validations] is not None:
            self.cross_validation = int(settings[ForecastConstant.cross_validations])
        if train_transform and self._pre_transform is None and settings is not None and len(settings) > 0:
            # Create a timeseries transform which is applied before data is passed to DNN
            feat_config = FeaturizationConfig()
            if settings.get("featurization_config"):
                feat_config = settings.get("featurization_config")
                del settings["featurization_config"]
            (
                forecasting_pipeline,
                ts_param_dict,
                lookback_removed,
                time_index_non_holiday_features
            ) = ml_engine.suggest_featurizers_timeseries(
                X_df,
                y_df,
                feat_config,
                settings,
                automl_transformer.TimeSeriesPipelineType.FULL
            )

            self._pre_transform = automl_transformer.TimeSeriesTransformer(
                forecasting_pipeline,
                automl_transformer.TimeSeriesPipelineType.FULL,
                feat_config,
                time_index_non_holiday_features,
                lookback_removed,
                **ts_param_dict
            )
            self._pre_transform.fit(X_df, y_df)
            if one_hot:
                get_encodings = True

        if self._pre_transform:
            X_transformed = self._pre_transform.transform(X_df, y_df)
            X_transformed = X_transformed.sort_index(axis=0)
            if ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN in X_transformed:
                y_df = X_transformed[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN]
            X_transformed = self._drop_extra_columns(X_transformed)
        else:
            X_transformed = X_df

        if isinstance(horizon, str) and self._pre_transform is not None:
            horizon = self._pre_transform.max_horizon
            self.horizon = horizon

        if get_encodings:
            encodings = self._get_embedding(X_transformed)

        self.dset_config = DataSourceConfig(feature_channels=X_transformed.shape[1],
                                            forecast_channels=1,
                                            encodings=encodings)

        self._data_grains = []
        grains = settings.get(ForecastConstant.grain_column_names, None) if settings else None
        if grains is not None:
            if isinstance(grains, str):
                grains = [grains]
            self.grain_col_info = []
            # Get the data needed for embedding.
            # column name prefix of the transformed grains
            # grain column prefix and seperator from transformer.
            if self._pre_transform and self._pre_transform.pipeline:
                grain_index_featurizer = [a[1] for a in self._pre_transform.pipeline.steps
                                          if isinstance(a[1], automl_transformer.GrainIndexFeaturizer)]
                if grain_index_featurizer:
                    grain_feature_prefix = grain_index_featurizer[0].grain_feature_prefix
                    grain_feature_prefix_sep = grain_index_featurizer[0].prefix_sep
                    for grain_name in grains:
                        # Collect the index and dimension of the grain.
                        transformed_grain_name = grain_feature_prefix + grain_feature_prefix_sep + grain_name
                        grain_column_info = GrainColumnInfo(grain_name,
                                                            X_transformed.columns.get_loc(transformed_grain_name),
                                                            len(X_transformed[transformed_grain_name].unique()))
                        self.grain_col_info.append(grain_column_info)

            assert ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN not in X_transformed
            X_transformed.insert(0, ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN,
                                 y_df.values)
            groupby = X_transformed.groupby(grains)
            for grain in groupby.groups:
                X_df = groupby.get_group(grain)
                y_df = X_df[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN]
                y = y_df.values
                y = y.reshape((1, y.shape[0]))
                self._data_grains.append(_DataGrainItem(X_df, y))
        else:
            X_transformed.insert(0, ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN,
                                 y_df.values)
            y = y_df.values
            y = y.reshape((1, y.shape[0]))
            self._data_grains.append(_DataGrainItem(X_transformed, y))

        self.has_past_regressors = has_past_regressors
        if self.sample_transform is None and not self.fetch_y_only:
            self.sample_transform = self._get_sample_transform(one_hot)

    def set_lookback(self, lookback: int) -> None:
        """
        Set lookback to be used with this dataset.

        :param lookback: Number of time steps used as input for forecasting.
        """
        self.lookback = lookback
        self._len = 0
        for item in self._data_grains:
            start_index = self._len
            size = self._get_size(item.y)
            self._len += size
            item.lookup_start_ix = start_index
            item.lookup_end_ix = self._len

    def get_last_lookback_items(self) -> pd.DataFrame:
        """Return the lookback items from each grain in dataset."""
        if not self._training_data:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, target="save_data", argument_name="X_dflow/y_dflow/settings")
            )
        if self.lookback is None:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, target="lookback", argument_name="lookback")
            )
        X_df, y_df, settings = self._training_data
        if settings is None:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, target="time_column", argument_name="settings")
            )
        X_df = X_df.copy()
        y_df = y_df.copy()
        grains, index = None, None
        assert ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN not in X_df
        X_df[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y_df.values
        if ForecastConstant.automl_constants.TimeSeries.TIME_COLUMN_NAME in settings:
            index = settings[ForecastConstant.automl_constants.TimeSeries.TIME_COLUMN_NAME]
            if ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES in settings:
                grains = settings[ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES]
        if index is None:
            ret_df = X_df[-self.lookback:]
        else:
            X_indexed = X_df.set_index(index)
            X_indexed = X_df.sort_index(axis=0)
            if grains:
                ret_df = X_indexed[0:0].reset_index()
                groupby = X_df.groupby(grains)
                for grain in groupby.groups:
                    X_df = groupby.get_group(grain)
                    ret_df = ret_df.append(X_df[-self.lookback:].reset_index())
            else:
                ret_df = X_df[-self.lookback:].reset_index()
        return ret_df[X_df.columns]

    def _get_size(self, y) -> None:
        """
        Set lookback to be used with this dataset.

        :param lookback: Number of time steps used as input for forecasting.
        """
        # If timeseries is smaller than lookback + horizon, we would need to pad
        if y.shape[-1] < self.lookback + self.horizon:
            sample_count = 1
        else:
            sample_count = (y.shape[-1] - self.lookback - self.horizon + self.step) // self.step
        return max(1, int(self.thinning * sample_count))

    def is_small_dataset(self) -> bool:
        """Return true if dataset is small."""
        if self._len is not None:
            return self._len < ForecastConstant.SMALL_DATASET_MAX_ROWS
        return True

    @staticmethod
    def _get_embedding(data: pd.DataFrame) -> List[EncodingSpec]:
        index = 0
        encodings = []
        column_purpose_detector = ColumnPurposeDetector()
        column_purpose = column_purpose_detector.get_raw_stats_and_column_purposes(data)
        for stats, featureType, name in column_purpose:
            if featureType == FeatureType.Categorical and stats.num_unique_vals > 2:
                # TODO remove this and replace this with label encoder
                max_num_features = int(data[name].max().astype(int) + 1)
                # embedding = EncodingSpec(feature_index=index, num_vals=stats.num_unique_vals)
                embedding = EncodingSpec(feature_index=index, num_vals=max_num_features)
                encodings.append(embedding)
            index = index + 1
        return encodings

    def _get_sample_transform(self, one_hot) -> tfs.ComposedTransform:
        if one_hot and self.dset_config.encodings:
            drop_first = False
            drop = True if drop_first else False
            tf_list = [tfs.OneHotEncode([e.feature_index for e in self.dset_config.encodings],
                                        [e.num_vals for e in self.dset_config.encodings],
                                        drop_first=drop),
                       tfs.OneHotEncode([e.feature_index for e in self.dset_config.encodings],
                                        [e.num_vals for e in self.dset_config.encodings],
                                        drop_first=drop,
                                        key=FUTURE_IND_KEY)]
            return tfs.ComposedTransform(tf_list)
        return None

    def __len__(self) -> int:
        """Return the number of samples in the dataset.

        :return: number of samples.
        """
        return self._len

    def feature_count(self) -> int:
        """Return the number of features in the dataset."""
        return self._data_grains[0].X.shape[0]

    @property
    def grain_count(self) -> int:
        """Return the number of grains in the dataset."""
        return len(self._data_grains)

    def suggest_embedding(self) -> bool:
        """Return if grain embeeding is needed."""
        if self.grain_count is None:
            ValidationException('time series dataset is not initialized with lookback')
        return self.grain_count >= self._min_grain_for_embedding

    def _get_test_size(self, grain_size, validation_percent):
        if self.cross_validation is not None:
            grain_test_size = self.cross_validation + self.horizon
            # Number of samples to be at least cv count to be included in validation set..
            if grain_size <= grain_test_size:
                grain_test_size = 0
        else:
            grain_test_size = max(1, math.floor(grain_size * validation_percent))
            if grain_size == grain_test_size:
                grain_test_size = 0
        return grain_test_size

    def get_train_test_split(self, validation_percent: float = 0.1):
        """
        Split the dataset into train and test as per the validtaion percent.

        :param validation_percent: percentage of data to be used as validation.
        """
        if self.lookback is None:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, target="lookback", argument_name="lookback")
            )
        train_size = 0
        test_size = 0
        test_data_grains = []
        train_data_grains = []
        step = 1 if self.cross_validation else self.horizon
        for item in self._data_grains:
            # total samples in the grain.
            grain_size = item.lookup_end_ix - item.lookup_start_ix
            grain_test_size = self._get_test_size(grain_size, validation_percent)
            grain_train_size = grain_size - grain_test_size
            train_item = _DataGrainItem(item.X_df, item.y, train_size, train_size + grain_train_size)
            train_size += grain_train_size
            train_data_grains.append(train_item)
            if grain_test_size > 0:
                if self.cross_validation:  # if cross validation and if enough data present then cv = test grain size.
                    grain_test_size = self.cross_validation
                else:
                    grain_test_size = max(1, math.ceil((grain_test_size - self.lookback) / step))

                # offset of test grain starts after the grain_train_size
                test_item = _DataGrainItem(item.X_df, item.y, test_size, test_size + grain_test_size,
                                           offset=grain_train_size)
                test_size += grain_test_size
                test_data_grains.append(test_item)

        train_dataset = TransformedTimeSeriesDataset(train_data_grains, self.horizon, self.lookback, train_size,
                                                     self.dset_config, self.step, self.has_past_regressors,
                                                     self.pre_transform, self.sample_transform, self.fetch_y_only)

        test_dataset = ValidationTimeSeriesDataset(test_data_grains, self.horizon, self.lookback, test_size,
                                                   self.dset_config, step, self.has_past_regressors,
                                                   self.pre_transform, self.sample_transform, self.fetch_y_only,
                                                   self.cross_validation)
        assert len(test_data_grains) <= len(train_data_grains)
        if len(test_data_grains) == 0:
            msg = "length of test grain {0}, train size = {1}".\
                format(len(test_data_grains), len(train_data_grains))
            assert len(test_data_grains) > 0, msg

        return train_dataset, test_dataset

    def __getitem__(self, idx: int) -> dict:
        """
        Get the idx-th training sample item from the dataset.

        :param idx: the item to get the sample.
        :return: returns the idx-th sample.
        """
        if self._len is None:
            raise ValidationException._with_error(AzureMLError.create(
                NotReady, argument_name="Dataset not initialized, lookback for the dataset is not set",
                target="lookback")
            )
        idx2, X, y = self._get_index_grain_from_lookup(idx)
        sample = self. _getitem_from_df(X, y, idx2)
        return sample

    def _get_data_grain_for_sample_idx(self, idx: int) -> _DataGrainItem:
        """
        Get the data grain corresponding to the idx-th sample index.

        This logic was pulled from / inspired by
        https://github.com/python/cpython/blob/6a1e9c26736259413b060b01d1cb52fcf82c0385/Lib/bisect.py#L26-L35.
        """
        lo = 0
        hi = len(self._data_grains)
        while lo < hi:
            mid = (lo + hi) // 2
            if idx < self._data_grains[mid].lookup_end_ix:
                hi = mid
            else:
                lo = mid + 1

        data_grain = self._data_grains[lo]
        Contract.assert_true(
            data_grain.lookup_start_ix <= idx < data_grain.lookup_end_ix,
            "Located data grain with lookup_start_idx ({}) and lookup_end_ix ({}) does not contain the \
                requested sample index ({}).".format(data_grain.lookup_start_ix, data_grain.lookup_end_ix, idx),
            log_safe=True)

        return data_grain

    def _get_index_grain_from_lookup(self, idx) -> tuple:
        located_grain = self._get_data_grain_for_sample_idx(idx)

        # lookup index from the grain is the offset +
        # steps size * distance to the index from lookup start.
        lookup_index = located_grain.offset + self.step * (idx - located_grain.lookup_start_ix)
        return lookup_index, located_grain.X, located_grain.y

    def _getitem_from_df(self, X, y, idx: int) -> dict:
        """
        Get the idx-th training sample item from the dataset.

        :param X: feature ndarray
        :param y: target array
        :param idx: the item to get the sample.
        :return: returns the idx-th sample.
        """
        # Get time series
        # The data values are transformed so the result is of the shape nfeatures X lookback for X
        # and 1 X horizon for y
        start_index = idx
        X_past = None
        X_fut = None
        if self.has_past_regressors:
            if X.shape[0] < self.lookback + self.horizon:
                X = X.T  # matrix transorm X as needed for training TCN.
                # If the time series is too short, zero-pad on the left
                if not self.fetch_y_only:
                    X_past = X[1:, :-self.horizon]
                    X_past = np.pad(
                        X_past,
                        pad_width=((0, 0), (self.lookback - X_past.shape[-1], 0)),
                        mode='constant',
                        constant_values=0
                    )
                    X_fut = X[1:, -self.horizon:]

                    X_past = torch.tensor(X_past.astype(np.float32), dtype=torch.float)
                    X_fut = torch.tensor(X_fut.astype(np.float32), dtype=torch.float)

                y_past = y[:, :-self.horizon]
                y_past = np.pad(
                    y_past,
                    pad_width=((0, 0), (self.lookback - y_past.shape[-1], 0)),
                    mode='constant',
                    constant_values=0
                )
                y_fut = y[:, -self.horizon:]

                y_past = torch.tensor(y_past.astype(np.float32), dtype=torch.float)
                y_fut = torch.tensor(y_fut.astype(np.float32), dtype=torch.float)
            else:
                end_index = start_index + self.lookback + self.horizon
                if not self.fetch_y_only:
                    X_item = X[start_index:end_index, 1:].T
                    X_past = torch.tensor(X_item[:, :self.lookback].astype(np.float32), dtype=torch.float)
                    X_fut = torch.tensor(X_item[:, self.lookback:].astype(np.float32), dtype=torch.float)

                y_item = y[:, start_index:end_index]
                y_past = torch.tensor(y_item[:, :self.lookback].astype(np.float32), dtype=torch.float)
                y_fut = torch.tensor(y_item[:, self.lookback:].astype(np.float32), dtype=torch.float)

            # Create the input and output for the sample
            if self.fetch_y_only:
                sample = {PAST_DEP_KEY: y_past,
                          FUTURE_DEP_KEY: y_fut}
            else:
                sample = {PAST_IND_KEY: X_past,
                          PAST_DEP_KEY: y_past,
                          FUTURE_IND_KEY: X_fut,
                          FUTURE_DEP_KEY: y_fut}
        else:
            X = None
            if not self.fetch_y_only:
                X_item = X[:, start_index:start_index + self.lookback]
                X = torch.tensor(X_item.astype(np.float32), dtype=torch.float)
            y_item = y[:, start_index + self.lookback:start_index + self.lookback + self.horizon]
            y = torch.tensor(y_item.astype(np.float32), dtype=torch.float)
            # Create the input and output for the sample
            sample = {'X': X, 'y': y}
        if self.sample_transform and not self.keep_untransformed:
            sample = self.sample_transform(sample)
        return sample


class TransformedTimeSeriesDataset(TimeSeriesDataset):
    """This class provides a dataset for based on automl transformed data and used in train test split."""

    def __init__(self, data_grains: List[_DataGrainItem],
                 horizon: int,
                 lookback: int,
                 len: int,
                 dset_config: DataSourceConfig,
                 step: int = 1,
                 has_past_regressors: bool = False,
                 pre_transform: automl_transformer.TimeSeriesTransformer = None,
                 sample_transform: Any = None,
                 fetch_y_only: bool = False):
        """
        Take a list of grains amd and provides access to windowed subseries for torch DNN training.

        :param data_grains : list of datagrains.
        :param horizon: Number of time steps to forecast.
        :param lookback: look back to use with in examples.
        :param len: number of samples in the grains.
        :param step: Time step size between consecutive examples.
        :param dset_config: dataset config
        :param has_past_regressors: data to populate past regressors for each sample
        :param pre_transform: pre_transformer to use
        :param sample_transform: feature transforms to use
        :param fetch_y_only: whether fetch_y_only
        """
        AbstractDNNTimeSeriesDataset.__init__(self,
                                              horizon,
                                              lookback,
                                              step=step,
                                              has_past_regressors=has_past_regressors,
                                              pre_transform=pre_transform,
                                              sample_transform=sample_transform,
                                              fetch_y_only=fetch_y_only,
                                              data_grains=data_grains,
                                              dset_config=dset_config)
        self._len = len


class _EvalDataset:
    """This class holds a X_valid,X_train, y_train, bin_info and ."""

    def __init__(self,
                 X_train: pd.DataFrame,
                 y_train: np.ndarray,
                 X_valid: pd.DataFrame,
                 y_valid: np.ndarray,
                 val_dataset: TimeSeriesDataset):
        """
        Create a structure needed to compute the metrics in automl.

        :param X_train: Transformed X_train.
        :param y_train: Transformed y_train.
        :param X_valid: Transformed X_valid.
        :param y_valid: Transformed y_valid.
        :param val_dataset: TIme series dataet that contains one horizon per grain to evaluate or the whole dataset.
        """
        self.X_train = X_train
        self.y_train = y_train
        self.X_valid = X_valid
        self.y_valid = y_valid
        self.val_dataset = val_dataset

        self.bin_info = binning.make_dataset_bins(self.y_valid.shape[-1], self.y_valid)
        y_sum = np.sum(y_train) + np.sum(y_valid)
        y_sum_square = np.sum(y_train ** 2) + np.sum(y_valid ** 2)
        y_count = float(len(y_train) + len(y_valid))
        self.y_std = math.sqrt((y_sum_square / y_count) - (y_sum / y_count) ** 2)
        self.y_min = min(y_train.min(), y_valid.min())
        self.y_max = min(y_train.max(), y_valid.max())
        self.pre_transforms = val_dataset._pre_transform

    def get_transformer(self, tranformer_name):
        return self.pre_transforms

    def get_y_range(self):
        return self.y_min, self.y_max

    def is_timeseries(self):
        return True

    def get_bin_info(self):
        return self.bin_info

    def get_y_std(self):
        return self.y_std

    def get_y_transformer(self):
        return None


class AbstractValidationTimeSeriesDataset(TransformedTimeSeriesDataset):
    """This class provides a dataset for validation and metric calculations, contains X_Train, y_train."""

    def get_eval_dataset(self, cv_index=None):
        """
        Get the evaluation dataset that contains the X_train/X_valid etc for metric calculations.

        :param cv_index : The item in the cv spit to use for prediction
                          /traing is done once excluding all test grains in it.
        :return: returns an _EvalDataset.
        """
        raise NotImplementedError()

    @staticmethod
    def create_eval_dataset(X_train_list: List[pd.DataFrame], X_valid_list: List[pd.DataFrame],
                            tsds: TimeSeriesDataset):
        """
        Create the evaluation dataset that contains the X_train/X_valid etc for metric calculations.

        :param X_train_list : list of dataframe containing X_train grains.
        :param X_valid_list : list of dataframe containing X_valid grains.
        :param tsds : A Timeseries that would give the predicted value of the y_valid.
        :return: returns an _EvalDataset.
        """
        X_train, y_train = AbstractValidationTimeSeriesDataset._get_X_y(X_train_list)
        X_valid, y_valid = AbstractValidationTimeSeriesDataset._get_X_y(X_valid_list)
        return _EvalDataset(X_train, y_train, X_valid, y_valid, tsds)

    @staticmethod
    def _get_X_y(X_list: List[pd.DataFrame]):
        target_column_name = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        df = pd.concat(X_list)
        X = df.drop(target_column_name, axis=1)
        y = df[target_column_name].values
        return X, y


class ValidationTimeSeriesDatasetFromTrainValid(AbstractValidationTimeSeriesDataset):
    """This class provides a dataset for validation and metric calculations, contains X_Train, y_train."""

    def __init__(self, X_train: TimeSeriesDataset, X_valid: TimeSeriesDataset):
        """
        Take a X_train and X_test and provide an evaluation dataset for evalutaion and metric compute.

        :param X_train : list of datagrains.
        :param X_valid: .
        """
        self.cross_validation = False
        self.X_valid = X_valid
        self.X_train = X_train

        TransformedTimeSeriesDataset.__init__(self,
                                              X_valid._data_grains,
                                              X_train.horizon,
                                              X_train.lookback,
                                              X_valid._len,
                                              X_valid.dset_config,
                                              step=X_valid.step,
                                              has_past_regressors=X_train.has_past_regressors,
                                              pre_transform=X_train.pre_transform,
                                              sample_transform=X_train.sample_transform,
                                              fetch_y_only=X_valid.fetch_y_only)

    def get_eval_dataset(self, cv_index: int = None):
        """
        Get the evaluation dataset that contains the X_train/X_valid etc for metric calculations.

        :param cv_index : The item in the cv spit to use for prediction
                          /traing is done once excluding all test grains in it.
        :return: returns an _EvalDataset.
        """
        X_train_list = []
        X_valid_list = []

        for item in self.X_train._data_grains:
            train_grain = item.X_df
            X_train_list.append(train_grain)

        for item in self.X_valid._data_grains:
            start_index = self.lookback
            end_index = start_index + self._len * self.horizon
            valid_grain = item.X_df
            if valid_grain.shape[0] > start_index + self.horizon:
                valid_grain = item.X_df.iloc[start_index : end_index]
            else:
                valid_grain = valid_grain.iloc[-self.horizon :]
            X_valid_list.append(valid_grain)

        return AbstractValidationTimeSeriesDataset.create_eval_dataset(X_train_list, X_valid_list, self.X_valid)


class ValidationTimeSeriesDataset(AbstractValidationTimeSeriesDataset):
    """This class provides a dataset for validation and metric calculations, contains X_Train, y_train."""

    def __init__(self, data_grains: List[_DataGrainItem],
                 horizon: int,
                 lookback: int,
                 len: int,
                 dset_config: DataSourceConfig,
                 step: int = 1,
                 has_past_regressors: bool = False,
                 pre_transform: automl_transformer.TimeSeriesTransformer = None,
                 transform: Any = None,
                 fetch_y_only: bool = False,
                 cross_validation: int = None):
        """
        Take a list of grains amd and provides access to windowed subseries for torch DNN training.

        :param data_grains : list of datagrains.
        :param horizon: Number of time steps to forecast.
        :param lookback: look back to use with in examples.
        :param len: number of samples in the grains.
        :param step: Time step size between consecutive examples.
        :param dset_config: dataset config
        :param has_past_regressors: data to populate past regressors for each sample
        :param pre_transform: pre_transformer to use
        :param transform: feature transforms to use
        :param fetch_y_only: whether fetch_y_only
        :param cross_validation: cros validation secified
        """
        TransformedTimeSeriesDataset.__init__(self,
                                              data_grains,
                                              horizon,
                                              lookback,
                                              len,
                                              dset_config,
                                              step,
                                              has_past_regressors,
                                              pre_transform,
                                              transform,
                                              fetch_y_only)
        self.cross_validation = cross_validation

    def get_eval_dataset(self, cv_index: int = None):
        """
        Get the evaluation dataset that contains the X_train/X_valid etc for metric calculations.

        :param cv_index : The item in the cv spit to use for prediction
                          /traing is done once excluding all test grains in it.
        :return: returns an _EvalDataset.
        """
        X_train_list = []
        X_valid_list = []
        new_grains = []
        val_len = 0
        if self.cross_validation:
            Contract.assert_true(cv_index < self.cross_validation or cv_index <= 0,
                                 "cv_index {} is out of range for cross_validation {}."
                                 .format(cv_index, self.cross_validation),
                                 log_safe=True)
        else:
            Contract.assert_true(cv_index is None,
                                 "cv_index {} is passed when cv is not used while creating dataset."
                                 .format(cv_index),
                                 log_safe=True)
        for item in self._data_grains:
            if cv_index is None:
                # tcn prediction starts after the lookup(context), offset is separating the training samples from test.
                val_start_index = item.offset + self.lookback
                val_end_index = val_start_index + (item.lookup_end_ix - item.lookup_start_ix) * self.horizon
            else:
                # if cv prediction is there are cv + horizon - 1 rows left for validation
                # for each cv one horizon per grain is predicted and slide by one row for next prediction.
                val_start_index = item.offset + self.lookback + cv_index  # target one horizon location for this grain.
                val_end_index = val_start_index + self.horizon  # look only one horizon.
                # create a new item to create a new dataset iterator that releases one sample per grain.
                val_item = _DataGrainItem(item.X_df, item.y, val_len, val_len + 1, item.offset + cv_index)
                new_grains.append(val_item)
                val_len = val_len + 1
            train_grain = item.X_df.iloc[: val_start_index]
            valid_grain = item.X_df.iloc[val_start_index : val_end_index]
            X_train_list.append(train_grain)
            X_valid_list.append(valid_grain)

        if cv_index is not None:
            tsds = TransformedTimeSeriesDataset(new_grains, self.horizon, self.lookback, val_len,
                                                self.dset_config, 1, self.has_past_regressors,
                                                self.pre_transform, self.transform, self.fetch_y_only)
        else:
            tsds = self
        return AbstractValidationTimeSeriesDataset.create_eval_dataset(X_train_list, X_valid_list, tsds)


class TimeSeriesInferenceDataset(TimeSeriesDataset):
    """This class provides a dataset for training timeseries model with dataprep features and label."""

    def __init__(self,
                 X_dflow: DataInputType,
                 y_dflow: Optional[TargetInputType],
                 saved_data: pd.DataFrame,
                 horizon: int,
                 lookback: int,
                 dset_config: DataSourceConfig,
                 has_past_regressors: bool = False,
                 pre_transform: automl_transformer.TimeSeriesTransformer = None,
                 sample_transform: Any = None,
                 **settings: Any):
        """
        Take a inference data(X) and label(y) and provide the last item from each grain.

        :param X_dflow: Training features in DataPrep DataFlow form(numeric data of shape(row_count, feature_count).
        :param y_dflow: Training label in DataPrep DataFlow for with shape(row_count, 1) or None.
        :param saved_data: Pandas Dataframe of last look back items from training data.
        :param horizon: Number of time steps to forecast.
        :param lookback: lookback for the model.
        :param dset_config: dataset settings
        :param has_past_regressors: data to populate past regressors for each sample
        :param pre_transform: pre_transformer to use
        :param sample_transform: feature transforms to use
        :param settings: automl timeseries settings for pre_transform
        """
        AbstractDNNTimeSeriesDataset.__init__(self,
                                              horizon,
                                              lookback,
                                              step=1,
                                              has_past_regressors=has_past_regressors,
                                              pre_transform=pre_transform,
                                              sample_transform=sample_transform,
                                              fetch_y_only=False,
                                              dset_config=dset_config)

        dummy_target_column = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        if isinstance(X_dflow, pd.DataFrame):
            X_df = X_dflow
        else:
            X_df = X_dflow.to_pandas_dataframe(extended_types=True)

        if y_dflow is None:  # Support None y value for the forecast.
            y_df = pd.DataFrame([np.nan] * X_df.shape[0])
        elif isinstance(y_dflow, np.ndarray) or isinstance(y_dflow, pd.Series):
            y_df = pd.DataFrame(y_dflow)
        elif isinstance(y_dflow, pd.DataFrame):
            y_df = y_dflow
        else:
            y_df = y_dflow.to_pandas_dataframe(extended_types=True)
        X_df = X_df.copy()
        y_df = y_df.copy()

        time_column = settings[ForecastConstant.time_column_name]
        target_column = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        X_df[target_column] = y_df.values
        self._X_orig = X_df.copy()
        if saved_data is not None:
            saved_indexed = saved_data.set_index(time_column)

        grains = None
        if ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES in settings:
            grains = settings[ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES]
        if grains is None:
            if X_df.shape[0] < self.lookback + self.horizon:
                min_time_value = min(X_df[time_column])
                X_df = X_df.append(saved_indexed[saved_indexed.index < min_time_value].reset_index()[X_df.columns])
                self._check_required_prediction_horizon(X_df, horizon, time_column, target_column)
            self._len = 1
        else:
            Xdf_indexed = X_df.set_index(time_column)
            Xdf_indexed = Xdf_indexed.sort_index(axis=0)
            Xdf_grains = Xdf_indexed.groupby(grains)
            saved_grains = saved_indexed.groupby(grains)
            grain_keys = Xdf_grains.groups.keys()
            saved_keys = saved_grains.groups.keys()
            self._len = 0
            for grain_key in grain_keys:
                self._len += 1
                grain_item = Xdf_grains.get_group(grain_key)
                self._check_required_prediction_horizon(grain_item.reset_index(), horizon, time_column, target_column)
                if grain_key in saved_keys:
                    if grain_item.shape[0] < self.lookback + self.horizon:
                        saved_item = saved_grains.get_group(grain_key)
                        min_time_value = min(grain_item.reset_index()[time_column])
                        X_df = X_df.append(saved_item[saved_item.index < min_time_value].reset_index()[X_df.columns])
        y_df = X_df.pop(ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN)
        X_transformed = X_df
        if self.pre_transform:
            X_transformed = self._pre_transform.transform(X_df, y_df.values)
            X_transformed = X_transformed.sort_index(axis=0)
            y_df = X_transformed[dummy_target_column]
            X_transformed = self._drop_extra_columns(X_transformed)

        # A list of every grain in the timeseries.
        # It is expected that grains are sorted in ascending order by lookup index.
        self._data_grains: List[_DataGrainItem] = []

        self._data_frames = []
        if dummy_target_column not in X_transformed.columns:
            X_transformed.insert(0, dummy_target_column, y_df.values)

        count_per_grain_needed = self.lookback + self.horizon
        index_columns = [time_column]
        if grains is None:
            y_item = y_df
            # set the index to last item.
            X_item = X_transformed[-(count_per_grain_needed):]
            y_item = y_item[-(count_per_grain_needed):]
            self._data_frames.append({"X": X_item, "y": y_item})

            self._data_grains.append(_DataGrainItem(X_item,
                                                    y_item.values.reshape(1, y_item.shape[0]),
                                                    0,
                                                    1,
                                                    0))
        else:
            index_columns.extend(grains)
            offset = 0
            X_transformed_grains = X_transformed.groupby(grains)
            transformed_grain_keys = X_transformed_grains.groups.keys()
            for grain_key in transformed_grain_keys:
                X_item = X_transformed_grains.get_group(grain_key)
                y_item = X_item[dummy_target_column]
                X_item = X_item[-(count_per_grain_needed):]
                y_item = y_item[-(count_per_grain_needed):]
                self._data_frames.append({"X": X_item, "y": y_item})
                self._data_grains.append(_DataGrainItem(X_item,
                                                        y_item.values.reshape(1, y_item.shape[0]),
                                                        offset,
                                                        offset + 1,
                                                        0))
                offset += 1

        # try to convert the time column to datatime
        if self._X_orig.dtypes[time_column] != np.dtype('datetime64[ns]'):
            try:
                self._X_orig[time_column] = pd.to_datetime(self._X_orig[time_column])
            except ValueError:
                pass
        self._X_orig.set_index(index_columns)
        self._index_columns = index_columns

    @staticmethod
    def _check_required_prediction_horizon(X_df, horizon, time_column, target_column):
        if np.any(np.isnan(X_df[target_column])):
            forecast_origin = min(X_df[X_df[target_column] is None or np.isnan(X_df[target_column])][time_column])
        else:
            raise DataException._with_error(AzureMLError.create(TimeseriesNothingToPredict))
        if X_df[X_df[time_column] >= forecast_origin].shape[0] > horizon:
            raise DataException._with_error(AzureMLError.create(ForecastHorizonExceeded, target="horizon"))

    def merge_results(self, y_pred: np.ndarray):
        """
        Get the idx-th training sample item from the dataset.

        :param X: feature ndarray
        :param y: target array
        :param idx: the item to get the sample.
        :return: returns the idx-th sample.
        """
        result = self._data_frames[0]['X'][0:0]
        target_column_name = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        for i, item in enumerate(self._data_frames):
            X = item['X'].copy()
            X[target_column_name][-self.horizon:] = y_pred[0][i].reshape(-1)
            result = result.append(X)
        if len(self._index_columns) == 1:  # no grains
            result = result.reset_index().set_index(self._index_columns)

        left, right = '_orig', '_pred'
        X_orig = self._X_orig.copy()
        merged = X_orig.join(result, on=self._index_columns, how='left', lsuffix=left, rsuffix=right)
        left_name = "{0}{1}".format(target_column_name, left)
        right_name = "{0}{1}".format(target_column_name, right)
        X_orig[target_column_name] = np.where(np.isnan(merged[left_name]), merged[right_name], merged[left_name])
        return X_orig.set_index(self._index_columns)
