# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module containing abstract class for DNNForecastWrapper and DNNParams."""
import copy
import logging
import sys

import numpy as np
import torch
from typing import Any, Dict, List, Optional
from torch.utils.data import DataLoader

from ..constants import ForecastConstant
from ..datasets.timeseries_datasets import TimeSeriesDataset, TimeSeriesInferenceDataset
from ..types import DataInputType, TargetInputType
from azureml.automl.core.shared.exceptions import ClientException
import azureml.automl.runtime.featurizer.transformer.timeseries as automl_transformer
from forecast.callbacks import CallbackList


class DNNParams:
    """This class is used in storing the DNN parameters for various forecast models."""

    def __init__(self,
                 required: List[str],
                 params: Dict[str, Any],
                 defaults: Optional[Dict[str, Any]] = None):
        """Initialize the object with required, default and passed in parameters.

        :param required: Required parameters for this Model, used in validation.
        :param params:  parameters passed.
        :param defaults: Default parameter if a required parameter is not passed.
        """
        self._required = required.copy() if required else {}
        self._params = params.copy() if params else {}
        self._data_for_inference = None
        self._init_defaults_for_missing_required_parameters(defaults if defaults else {})

    def set_parameter(self, name: str, value: Any) -> None:
        """Set the parameter with the passed in value.

        :param name: name of the parameter to set/update.
        :param value: value to set.
        :return: None
        """
        self._params[name] = value

    def _init_defaults_for_missing_required_parameters(self, defaults) -> None:
        """Set default values for missing required parameters.

        :return:
        """
        for name in self._required:
            if name not in self._params:
                if name in defaults:
                    self._params[name] = defaults[name]
                else:
                    raise ClientException("Required parameter '{0}' is missing.".format(name), has_pii=False)

    def get_value(self, name: str, default_value: Any = None) -> Any:
        """Get the value from the parameter or default dictionary.

        :param name: name of the parameter to get the values for.
        :param default_value: default value to use in case param is unset or not found
        :return:
        """
        if name in self._params:
            value = self._params.get(name)
            if value is None:
                value = default_value
            return value
        return default_value

    def __str__(self) -> str:
        """Return the string printable representation of the DNNParams.

        :return:
        """
        return str(self._params)


class DNNForecastWrapper(torch.nn.Module):
    """This is the abstract class for Forecast DNN Wrappers."""

    def __init__(self):
        """Initialize with defaults."""
        super().__init__()
        self.input_channels = None
        self.params = None
        self.model = None
        self.output_channels = 1
        self._pre_transform = None
        self._sample_transform = None
        self.forecaster = None
        self._data_for_inference = None

    def train(self, n_epochs: int, X: DataInputType = None, y: DataInputType = None,
              X_train: DataInputType = None, y_train: DataInputType = None,
              X_valid: DataInputType = None, y_valid: DataInputType = None,
              logger: logging.Logger = None) -> None:
        """Start the DNN training.

        :param n_epochs: number of epochs to try.
        :param X: full set of data for training.
        :param y: fullsetlabel for training.
        :param X_train: training data to use.
        :param y_train: validation data to use.
        :param X_valid: validation data to use.
        :param y_valid: validation target  data to use.
        :param logger: logger
        :return: Nothing, the model is trained.
        """
        raise NotImplementedError

    def predict(self, X: DataInputType, y: DataInputType, n_samples: int) -> np.ndarray:
        """Return the predictions for the passed in X and y values.

        :param X: data values
        :param y: label for look back and nan for the rest.
        :param n_samples:  number samples to be retured with each prediction.
        :return: a tuple containing one dimentional prediction of ndarray and tranformed X dataframe.
        """
        raise NotImplementedError

    def get_lookback(self):
        """Return the lookback."""
        raise NotImplementedError

    def forecast(self, X: DataInputType, y: Optional[TargetInputType] = None) -> tuple:
        """Return the predictions for the passed in X and y values.

        :param X: data values
        :param y: label for look back and nan for the rest.
        :param n_samples:  number samples to be retured with each prediction.
        :return: a ndarray of samples X rows X horizon
        """
        dummy_target_column_name = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        horizon = self.params.get_value(ForecastConstant.Horizon)
        looback = self.get_lookback()
        saved_data = self._data_for_inference
        inference_dataset = TimeSeriesInferenceDataset(X, y, saved_data, horizon, looback, None, True,
                                                       self._pre_transform, self._sample_transform,
                                                       **self.dataset_settings)
        y_pred_horizon = self._predict(inference_dataset)
        merged_prediction_df = inference_dataset.merge_results(y_pred_horizon)
        # Returns a vector of predictions and an index for the prediction.
        # classical returns the full dataframe not just index.
        y_return_value = merged_prediction_df[dummy_target_column_name].values
        index_for_return_value = merged_prediction_df
        return y_return_value, index_for_return_value

    def _forecast_no_grain(self, X: DataInputType, y: TargetInputType, grain) -> tuple:
        dummy_target_column_name = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        X[dummy_target_column_name] = y
        X_indexed = X.set_index(self.dataset_settings[ForecastConstant.time_column_name])
        y_indexed = X_indexed[dummy_target_column_name].values
        X = X.drop([dummy_target_column_name], axis=1)
        y_pred = self.predict(X, y, 1).reshape(-1)
        if self._pre_transform:
            X_tranformed = self._pre_transform.transform(X)
        else:
            X_tranformed = X_indexed

        total_size = X_tranformed.shape[0]
        predicted_size = y_pred.shape[0]
        if total_size < predicted_size:
            y_result = y_pred[:total_size]
        elif total_size == predicted_size:
            y_result = y_pred
        else:
            y_result = np.hstack([y_indexed[:(total_size - predicted_size)], y_pred])
        return y_result, X_tranformed

    def parse_parameters(self) -> DNNParams:
        """Parse parameters from command line.

        :return: returns the  DNN  param object from the command line arguments
        """
        raise NotImplementedError

    def init_model(self, settings: dict = None) -> None:
        """Initialize the model using the command line parse method.

        :param settings: automl settings such as lookback and horizon etc.
        :return:
        """
        self.params = self.parse_parameters()
        for item in settings if settings else {}:
            self.params.set_parameter(item, settings[item])

    def set_transforms(self, input_channels: int, pre_transform: automl_transformer.TimeSeriesTransformer = None,
                       sample_transform: Any = None) -> None:
        """Set the the training data set transformations and channels.

        :param input_channels: Number of features in tne dataset.
        :param pre_transform: automl timeseries transformations applied on training data set.
        :param sample_transform: transformations applied as part of tcn dataset processing.
        :return:
        """
        if self.input_channels is None:
            self.input_channels = input_channels

        if self._pre_transform is None:
            self._pre_transform = pre_transform

        if self._sample_transform is None:
            self._sample_transform = sample_transform

    def create_data_loader(self, ds: TimeSeriesDataset, batch_size: int) -> DataLoader:
        """Create the dataloader from time series dataset.

        :param ds: TimeseriesDataset
        :param batch_size:  batch size for the training.
        :return:
        """
        self.set_transforms(ds.feature_count(), ds.pre_transform, ds.sample_transform)

        num_cpu = self._get_num_workers_data_loader(dataset=ds)

        return DataLoader(
            ds,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_cpu,
            pin_memory=True)

    @staticmethod
    def _get_num_workers_data_loader(dataset: TimeSeriesDataset) -> int:
        """Get count of number of workers to use for loading data.

        :param dataset: TimeseriesDataset that will be loaded with num workers.
        :return: returns number of workers to use
        """
        # on win using num_workers causes spawn of processes which involves pickling
        # loading data in main process is faster in that case
        if sys.platform == 'win32':
            return 0
        num_cpu_core = None
        try:
            import psutil
            num_cpu_core = psutil.cpu_count(logical=False)
        except Exception:
            import os
            num_cpu_core = os.cpu_count()
            if num_cpu_core is not None:
                # heuristics assuming 2 hyperthreaded logical cores per physical core
                num_cpu_core /= 2

        if num_cpu_core is None:
            # Default to 0 to load data in main thread memory
            return 0
        else:
            return int(num_cpu_core)

    @staticmethod
    def get_arg_parser_name(arg_name: str):
        """Get the argument name needed for arg parse.(prefixed with --).

        :param arg_name: argument name to convert to argparser format.
        :return:

        """
        return "--{0}".format(arg_name)

    @property
    def dataset_settings(self):
        """Get data settings for data that model is trained on."""
        settings = self.params.get_value(ForecastConstant.dataset_settings)
        return settings if settings else {}

    @property
    def name(self):
        """Name of the Model."""
        raise NotImplementedError

    def __getstate__(self) -> Dict[str, Any]:
        """
        Get state pickle-able objects.

        :return: state
        """
        state = dict(self.__dict__)
        forecaster = copy.copy(state['forecaster'])

        # This is assuming that model callbacks are done doing anything once model is saved
        # If we want callbacks to do anything post model save, we need to change this code
        if forecaster is not None:
            forecaster._callbacks = CallbackList([], self.model)
            forecaster.device = 'cpu'
        state['forecaster'] = forecaster
        state['loss'] = None
        state['optimizer'] = None
        return state

    def __setstate__(self, state) -> None:
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        self.__dict__.update(state)
        self.forecaster.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.forecaster.device)
