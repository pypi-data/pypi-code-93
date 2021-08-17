# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating a model based on TCN."""
import argparse
import math
import os
import random
import logging
from typing import List

import numpy as np
import torch
from azureml.automl.core.shared._diagnostics.contract import Contract

from azureml.contrib.automl.dnn.forecasting._transforms import TCNBatchTransform
from azureml.core.run import Run
import azureml.automl.core   # noqa: F401
from azureml.automl.core.shared import logging_utilities
from .forecast_wrapper import DNNForecastWrapper, DNNParams
from .tcn_model_utl import build_canned_model
from ..constants import ForecastConstant, TCNForecastParameters
from ..callbacks.run_update import RunUpdateCallback
from ..datasets.timeseries_datasets import TimeSeriesDataset, GrainColumnInfo
from ..metrics.primary_metrics import get_supported_metrics
from ..types import DataInputType
from forecast.callbacks.callback import MetricCallback
from forecast.callbacks.optimizer import (  # noqa: F401
    EarlyStoppingCallback, LRScheduleCallback, ReduceLROnPlateauCallback
)
from forecast.data.sources.data_source import DataSourceConfig
from forecast.forecaster import Forecaster, ForecastingModel
from forecast.losses import QuantileLoss
from forecast.models.backbone.base import MultilevelType
from forecast.models.canned import create_tcn_quantile_forecaster
from forecast.utils import create_timestamped_dir


class ForecastTCNWrapper(DNNForecastWrapper):
    """Wrapper for TCN model adapted to work with automl Forecast Training."""

    required_params = [ForecastConstant.Learning_rate, ForecastConstant.Horizon, ForecastConstant.Lookback,
                       ForecastConstant.Batch_size, ForecastConstant.num_epochs, ForecastConstant.Loss,
                       ForecastConstant.Device, ForecastConstant.primary_metric]
    loss = QuantileLoss(ForecastConstant.QUANTILES)
    default_params = {ForecastConstant.Loss: loss,  # torch.distributions.StudentT,
                      ForecastConstant.Device: 'cuda' if torch.cuda.is_available() else 'cpu'}
    # configure our loss function

    def _init__(self):
        super().__init__()

    def train(self, n_epochs: int, X: DataInputType = None, y: DataInputType = None,
              X_train: DataInputType = None, y_train: DataInputType = None,
              X_valid: DataInputType = None, y_valid: DataInputType = None,
              logger: logging.Logger = None) -> None:
        """
        Start the DNN training.

        :param n_epochs: number of epochs to try.
        :param X: data for training.
        :param y: target data for training.
        :param X_train: training data to use.
        :param y_train: training target to use.
        :param X_valid: validation data to use.
        :param y_valid: validation target to use.
        :param logger: logger.
        """
        settings = self.dataset_settings
        num_samples = 0
        ds = None
        ds_train = None
        ds_valid = None
        run_update_callback = None
        horizon = self.params.get_value(ForecastConstant.Horizon)
        min_grain_for_embedding = self.params.get_value(TCNForecastParameters.MIN_GRAIN_SIZE_FOR_EMBEDDING,
                                                        TCNForecastParameters.MIN_GRAIN_SIZE_FOR_EMBEDDING_DEFAULT)
        if X_train is not None:
            ds_train = TimeSeriesDataset(X_dflow=X_train,
                                         y_dflow=y_train,
                                         horizon=horizon,
                                         step=1,
                                         has_past_regressors=True,
                                         one_hot=False,
                                         train_transform=True,
                                         save_last_lookback_data=True,
                                         min_grain_for_embedding=min_grain_for_embedding,
                                         **settings)
            if isinstance(self.params.get_value(ForecastConstant.Horizon), str):
                self.params.set_parameter(ForecastConstant.Horizon, ds_train.horizon)
            dset_config = ds_train.dset_config
        else:
            assert X is not None
            assert y is not None
            ds = TimeSeriesDataset(X_dflow=X,
                                   y_dflow=y,
                                   horizon=horizon,
                                   step=1,
                                   has_past_regressors=True,
                                   one_hot=False,
                                   train_transform=True,
                                   save_last_lookback_data=True,
                                   min_grain_for_embedding=min_grain_for_embedding,
                                   **settings)
            if isinstance(self.params.get_value(ForecastConstant.Horizon), str):
                self.params.set_parameter(ForecastConstant.Horizon, ds.horizon)
            dset_config = ds.dset_config

        if logger is None:
            logger = logging_utilities.get_logger()
        dataset_to_prepare = ds if ds is not None else ds_train
        if self.model is None or self.forecaster is None:
            run_update_callback = self._create_runupdate_callback(X_valid, y_valid, logger)
            # set the grain info if embedding is needed from the model
            grains_info = dataset_to_prepare.grain_col_info if dataset_to_prepare.suggest_embedding() else None
            self._build_model_forecaster(run_update_callback, dset_config, logger, grains_info)
        # set the lookback as the receptive field of the model for the dataset
        dataset_to_prepare.set_lookback(self.model.receptive_field)
        num_samples = len(dataset_to_prepare)
        # set the transformations used along with the wrapper, so can be used during validation and inference.
        self.set_transforms(dataset_to_prepare.feature_count(), dataset_to_prepare.pre_transform,
                            dataset_to_prepare.sample_transform)
        if ds_train:
            ds_valid = self._get_timeseries(X_valid, y_valid)
        else:
            ds_train, ds_valid = ds.get_train_test_split()

        if run_update_callback:
            run_update_callback.set_evaluation_dataset(ds_train, ds_valid)

        fraction_samples = math.floor(num_samples * 0.05)
        if fraction_samples <= 1:
            batch_size = 1
        else:
            batch_size = int(math.pow(2, math.floor(math.log(fraction_samples, 2)))) \
                if fraction_samples < 1024 else 1024
        while True:
            Contract.assert_true(batch_size > 0,
                                 "Cannot proceed with batch_size: {}".format(batch_size), log_safe=True)
            try:
                logger.info("Trying with batch_size: {}".format(batch_size))
                self._data_for_inference = dataset_to_prepare.get_last_lookback_items()
                dataloader_train = self.create_data_loader(ds_train, batch_size)
                dataloader_valid = self.create_data_loader(ds_valid, batch_size)

                self.forecaster.fit(
                    dataloader_train=dataloader_train,
                    loss=self.loss,
                    optimizer=self.optimizer,
                    epochs=n_epochs,
                    dataloader_val=dataloader_valid)
                break
            except RuntimeError as e:
                if 'out of memory' in str(e):
                    logger.info("Couldn't allocate memory for batch_size: {}".format(batch_size))
                    batch_size = batch_size // 2
                else:
                    raise e

        self.batch_size = batch_size
        # At the end of the training upload the tabular metric and model.
        if run_update_callback:
            run_update_callback.upload_model_and_tabular_metrics()

    def _create_runupdate_callback(self, X_valid: DataInputType, y_valid: DataInputType,
                                   logger: logging.Logger) -> RunUpdateCallback:
        # get the Azure ML run object
        run_context = Run.get_context()
        return RunUpdateCallback(model_wrapper=self, run_context=run_context, params=self.params)

    def _build_model_forecaster(self, run_update_callback: RunUpdateCallback,
                                dset_config: DataSourceConfig, logger: logging.Logger,
                                grain_column_info: List[GrainColumnInfo]) -> None:
        # create a model based on the hyper parameters.
        self.model = build_canned_model(params=self.params, dset_config=dset_config,
                                        horizon=self.params.get_value(ForecastConstant.Horizon),
                                        num_quantiles=len(ForecastConstant.QUANTILES), logger=logger,
                                        grain_column_info=grain_column_info)

        # checkpoint directory to save model state.
        chkpt_base = create_timestamped_dir('./chkpts')
        out_dir = create_timestamped_dir(chkpt_base)
        self.model.to_json(os.path.join(out_dir, 'model_arch.json'))

        # set callbacks.
        lr = self.params.get_value(ForecastConstant.Learning_rate, 0.001)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        # number epochs to wait before early stopping evaluation start.
        self.patience = self.params.get_value(TCNForecastParameters.EARLY_STOPPING_DELAY_STEPS,
                                              TCNForecastParameters.EARLY_STOPPING_DELAY_STEPS_DEFAULT)
        # learning rate reduction with adam optimizer
        self.lr_factor = self.params.get_value(TCNForecastParameters.LR_DECAY_FACTOR,
                                               TCNForecastParameters.LR_DECAY_FACTOR_DEFAULT)
        lr_sched = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, patience=int(self.patience / 2),
                                                              factor=self.lr_factor)
        # minimum improvement from the previous epoch to continue experiment, we are using relative improvement.
        self.min_improvement = self.params.get_value(TCNForecastParameters.EARLY_STOPPING_MIN_IMPROVEMENTS,
                                                     TCNForecastParameters.EARLY_STOPPING_MIN_IMPROVEMENTS_DEFAULT)
        # metric to use for early stopping.
        metric = self.params.get_value(ForecastConstant.primary_metric, ForecastConstant.DEFAULT_EARLY_TERM_METRIC)
        if metric not in get_supported_metrics():
            metric = ForecastConstant.DEFAULT_EARLY_TERM_METRIC
            logger.warn(f'Selected primary metric is not supported for early stopping, using {metric} instead')

        # metric object that computes the training and validation metric
        train_valid_metrics = {metric: get_supported_metrics()[metric]}
        callbacks = [
            MetricCallback(train_valid_metrics, train_valid_metrics),
            run_update_callback,
            # LR reduction was performing with loss metric than any of the custom metric specified.
            ReduceLROnPlateauCallback(lr_sched, ForecastConstant.Loss),
            EarlyStoppingCallback(patience=self.patience, min_improvement=self.min_improvement, metric=metric)
        ]
        logger.info(f'the name of the metric used EarlyStoppingCallback {metric}')
        logger.info(f'The patience used in used EarlyStoppingCallback {self.patience}')
        logger.info(f'the name of the improvement passed to EarlyStoppingCallback {self.min_improvement}')
        logger.info(f'LR Factor {self.lr_factor}')

        # set up the model for training.
        self.forecaster = Forecaster(model=self.model,
                                     device=self.params.get_value(ForecastConstant.Device),
                                     metrics=train_valid_metrics,
                                     callbacks=callbacks,
                                     batch_transform_type=TCNBatchTransform)

    def predict(self, X: DataInputType, y: DataInputType, n_samples: int = 1) -> np.ndarray:
        """
        Return the predictions for the passed in `X` and `y` values.

        :param X: data values.
        :param y: label for look back and nan for the rest.
        :param n_samples: number of samples to be returned with each prediction.
        :return: numpy ndarray with shape (n_samples, n_rows, horizon).
        """
        ds = self._get_timeseries(X, y)
        return self._predict(ds)

    def _get_timeseries(self, X: DataInputType, y: DataInputType, step: str = None) -> TimeSeriesDataset:
        """
        Get timeseries for given inputs and set_lookback for model.

        :param X: data values
        :param y: label for lookback and nan for rest
        :param n_samples: number of samples to be returned with each prediction.
        :param step: number of samples to skip to get to the next block of data(lookback+horzon)
        :return: Timeseries dataset
        """
        if step is None:
            step = self.params.get_value(ForecastConstant.Horizon)
        ds = TimeSeriesDataset(X_dflow=X,
                               y_dflow=y,
                               horizon=self.params.get_value(ForecastConstant.Horizon),
                               step=step,
                               has_past_regressors=True,
                               one_hot=False,
                               pre_transform=self._pre_transform,
                               sample_transform=self._sample_transform,
                               **self.dataset_settings)
        ds.set_lookback(self.model.receptive_field)
        return ds

    def _predict(self, ds: TimeSeriesDataset, n_samples: int = 1) -> np.ndarray:
        """
        Return the predictions for the passed timeseries dataset.

        :param ds: TimeSeriesDataset to use for prediction.
        :param n_samples:  number of samples to be returned with each prediction.
        :return: numpy ndarray with shape (n_samples, n_rows, horizon).
        """
        dataloader_test = self.create_data_loader(ds, self.params.get_value(ForecastConstant.Batch_size))

        predictions = np.asarray(self.forecaster.predict(dataloader_test))
        # Currently returning only one prediction: median
        return_predict_index = predictions.shape[0] // 2
        return predictions[return_predict_index:return_predict_index + 1]

    def get_lookback(self):
        """Get lookback used by model."""
        if self.model is not None:
            return self.model.receptive_field
        else:
            return self.params.get_value(ForecastConstant.Lookback)

    @property
    def name(self):
        """Name of the Model."""
        return ForecastConstant.ForecastTCN

    def parse_parameters(self) -> DNNParams:
        """
        Parse parameters from command line.

        return: returns the  DNN  param object from the command line arguments
        """
        parser = argparse.ArgumentParser()

        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.num_epochs), type=int,
                            default=25, help='number of epochs to train')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Lookback), type=int,
                            default=8, help='lookback for model')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Horizon), type=int,
                            default=4, help='horizon for prediction')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Batch_size), type=int,
                            default=8, help='batch_size for training')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.primary_metric), type=str,
                            default='', help='primary metric for training')

        # Model hyper-parameters
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Learning_rate), type=float,
                            default=0.001, help='learning rate')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.NUM_CELLS), type=int,
                            help='num cells')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.MULTILEVEL), type=str,
                            help='multilevel')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.DEPTH), type=int,
                            help='depth')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.NUM_CHANNELS), type=int,
                            help='number of channels')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.DROPOUT_RATE), type=float,
                            help='dropout rate')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.DILATION), type=int,
                            default=TCNForecastParameters.DILATION_DEFAULT, help='tcn dilation')

        # EarlyStopping Parameters
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.EARLY_STOPPING_MIN_IMPROVEMENTS),
                            type=float,
                            default=TCNForecastParameters.EARLY_STOPPING_MIN_IMPROVEMENTS_DEFAULT,
                            help='min improvement required between epochs to continue training')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.LR_DECAY_FACTOR),
                            type=float,
                            default=TCNForecastParameters.LR_DECAY_FACTOR_DEFAULT,
                            help='LR decay factor used in reducing Learning Rate by LR schedular.')

        # Embedding defaults
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.MIN_GRAIN_SIZE_FOR_EMBEDDING),
                            type=int,
                            default=TCNForecastParameters.MIN_GRAIN_SIZE_FOR_EMBEDDING_DEFAULT,
                            help='min grain size to enable grain embedding')
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.EMBEDDING_TARGET_CALC_TYPE),
                            type=str,
                            default=TCNForecastParameters.EMBEDDING_TARGET_CALC_TYPE_DEFAULT,
                            help='method to use when computing embedding output size')
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.EMBEDDING_MULT_FACTOR),
                            type=float,
                            default=TCNForecastParameters.EMBEDDING_MULT_FACTOR_DEFAULT,
                            help='multiplaction factor to use output size when MULT method is selected')
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.EMBEDDING_ROOT),
                            type=float,
                            default=TCNForecastParameters.EMBEDDING_ROOT_DEFAULT,
                            help='the number to use as nth root for output sise when ROOT method is selectd')

        args, unknown = parser.parse_known_args()
        arg_dict = vars(args)
        arg_dict[ForecastConstant.n_layers] = max(int(math.log2(args.lookback)), 1)
        dnn_params = DNNParams(ForecastTCNWrapper.required_params, arg_dict, ForecastTCNWrapper.default_params)
        return dnn_params

    def __getstate__(self):
        """
        Get state picklable objects.

        :return: state
        """
        return super(ForecastTCNWrapper, self).__getstate__()

    def __setstate__(self, state):
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        super(ForecastTCNWrapper, self).__setstate__(state)
