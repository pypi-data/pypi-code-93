# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Optional, Tuple, Union, cast
import datetime
import logging
import os
import tempfile

import numpy as np
import pandas as pd
from azureml.automl.core import dataset_utilities
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import PredictionException
from azureml.automl.runtime import _data_splitting_utilities
from azureml.automl.runtime._data_definition import MaterializedTabularData
from azureml.automl.runtime.shared import metrics
from azureml.core import Run, Dataset, Datastore
from azureml.data.abstract_dataset import AbstractDataset
from azureml.data.constants import WORKSPACE_BLOB_DATASTORE
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl._model_download_utilities import _download_automl_model
from azureml.train.automl.model_proxy import RESULTS_PROPERTY
from azureml.train.automl.runtime._data_preparer import DataPreparerFactory, DatasetType

OUTPUT_FILE_NAME_TEMPLATE = "predictions{}.csv"


logger = logging.getLogger(__name__)


def get_model_from_training_run(experiment, training_run_id):
    """
    Get the fitted model from the specified training run.

    :param experiment: The experiment which contains the training run.
    :param training_run_id: The id for the AutoML child run which contains the model.
    :return: The fitted model
    """
    logger.info("Fetching model from training run.")
    training_run = Run(experiment, training_run_id)
    fitted_model = _download_automl_model(training_run)
    return fitted_model


def get_target_metrics(task, is_timeseries):
    """
    Get the types of metrics which should
    be computed for the specified task.

    :param task: The task type (see constants.py).
    :param is_timeseries: Whether this is a timeseries run or not
    :return: A list of metric types
    """
    # TODO: the metrics methods are deprecated.
    # Used here to mimic the behavior of pipeline_run_helper.run_pipeline()
    # Note, the default target metrics used in ClientRunner
    # (scoring_utilities.get_scalar_metrics(task))
    # do not return the metrics graphs.
    # Metrics.get_default_metrics(task) does return the graphs data.
    target_metrics = metrics.get_default_metrics(task)
    if is_timeseries:
        target_metrics += metrics.get_default_metrics(constants.Subtasks.FORECASTING)
    return target_metrics


def get_test_datasets_from_dataprep_json(
        dataprep_json: str,
        automl_settings: AzureAutoMLSettings) -> Tuple[Optional[pd.DataFrame],
                                                       Optional[np.ndarray]]:
    """
    Get the materialized test dataset which is specified in the given dataprepjson.
    The dataprep_json format is the same as is passed in to Jasmine when creating a
    new AutoML run. If a train/test split was performed during the main AutoML run,
    then the dataprep_json must also contain a reference to the training_data.
    The expected root level keys in dataprep_json which correspond to the datasets are:
        "test_data" and "training_data" (the latter is only required when splitting).

    :param dataprep_json: The dataprep json which contains a reference to the test dataset.
    :param automl_settings: AzureAutoMLSettings for the parent run.
    :return: A Tuple containing (X_test, y_test)
    """
    X_test, y_test = None, None
    preparer = DataPreparerFactory.get_preparer(dataprep_json)

    if preparer.has_test_data():
        raw_data = preparer.prepare_raw_experiment_data(automl_settings, [DatasetType.Test])
        X_test = raw_data.X_test
        y_test = raw_data.y_test

    elif automl_settings.test_size > 0.0:
        raw_data = preparer.prepare_raw_experiment_data(automl_settings, [DatasetType.FitParams])
        tabular_data = MaterializedTabularData(raw_data.X, raw_data.y, raw_data.weights)
        _, test_data = _data_splitting_utilities.split_dataset(
            tabular_data, automl_settings.task_type, automl_settings.test_size)
        X_test = test_data.X
        y_test = test_data.y

    Contract.assert_value(X_test, "X_test")
    return X_test, y_test


def _get_pandas(results):
    if results is None:
        raise Exception("Inferencing returned no results.")
    elif isinstance(results, pd.DataFrame):
        logger.info("Inference output as pandas.")
        return results
    elif isinstance(results, AbstractDataset):
        logger.info("Inference output as AbstractDataset, casting to pandas.")
        return results.to_pandas_dataframe()
    else:
        # if its not any of the above types, assume its some primitive array type that pandas can accept
        logger.info("Inference output is not pandas or AbstractDataset, casting to pandas.")
        return pd.DataFrame(results)


def _save_results(results, run):
    """
    Save the prediction(s) to the default datastore.
    """
    logger.info("Saving predicted results.")

    if isinstance(results, tuple) or isinstance(results, list):
        logger.info("Multiple inference outputs, casting to pandas.")
        results_pd = [_get_pandas(result) for result in results]
    else:
        logger.info("Single inference output, casting to pandas.")
        results_pd = [_get_pandas(results)]

    local_paths = []
    remote_paths = []

    with tempfile.TemporaryDirectory() as project_folder:
        if len(results_pd) > 1:
            max_chars = len(str(len(results_pd)))

            for i, df in enumerate(results_pd, start=1):
                suffix = "_" + str(i).zfill(max_chars)
                file_name = OUTPUT_FILE_NAME_TEMPLATE.format(suffix)
                local_path = os.path.join(project_folder, file_name)
                local_paths.append((file_name, local_path))

                df.to_csv(local_path, index=False)
        else:
            file_name = OUTPUT_FILE_NAME_TEMPLATE.format("")
            local_path = os.path.join(project_folder, file_name)
            local_paths.append((file_name, local_path))

            results_pd[0].to_csv(local_path, index=False)

        # Upload the local files as run artifacts
        for path in local_paths:
            target_path = os.path.join('predictions', path[0])
            upload_result = run.upload_file(name=target_path,
                                            path_or_stream=path[1],
                                            datastore_name=WORKSPACE_BLOB_DATASTORE)
            for item in upload_result.artifacts.values():
                remote_path = item.artifact_id
                remote_paths.append(remote_path)
                logger.info("Uploaded result to {}".format(remote_path))

        datastore = Datastore.get(run.experiment.workspace, WORKSPACE_BLOB_DATASTORE)

        for remote_path in remote_paths:
            # Mark the output files as "output datasets" for the run.
            # This happens in the ensure_saved method.
            dataset = Dataset.Tabular.from_delimited_files(datastore.path(remote_path))
            dataset_utilities.ensure_saved(run.experiment.workspace, output_data=dataset)

        run.add_properties({RESULTS_PROPERTY: str(remote_paths)})


def inference(task: str,
              model: Any,
              X_test: pd.DataFrame,
              y_context: Optional[Union[pd.DataFrame, np.ndarray]] = None,
              is_timeseries: bool = False) -> Tuple[Union[pd.DataFrame, np.ndarray],
                                                    np.ndarray,
                                                    Optional[pd.DataFrame]]:
    """
    Return predictions from the given model with a provided task type.

    :param task: The task type (see constants.py).
    :param model: The model used to make predictions.
    :param X_test: The inputs on which to predict.
    :param y_context: Used for forecasting. The target value combining definite
                      values for y_past and missing values for Y_future.
                      If None the predictions will be made for every X_pred.
    :param is_timeseries: Whether or not this is a forecasting task.
    :return: The predictions of the model on X_test
        The shape of the array returned depends on the task type
        Classification will return probabilities for each class.
        If a forecasting prediction was performed then the third value
        in the tuple will be set to the X transformed by the forecast method
        which can be used for computing the metrics. Otherwise, the third
        value will be None.
    """
    with log_utils.log_activity(logger, activity_name=constants.TelemetryConstants.PREDICT_NAME):
        X_forecast_transformed = None

        if task == constants.Tasks.CLASSIFICATION:
            y_pred = model.predict_proba(X_test)

            # If the predicted result is an ndarray and thus does
            # not contain column headers then convert the ndarray
            # to a pandas DataFrame using the correct headers.
            if isinstance(y_pred, np.ndarray):
                Contract.assert_true(
                    hasattr(model, 'classes_') and len(model.classes_) > 0,
                    message="Model {} missing required attribute classes_".format(type(model).__name__),
                    target="inference",
                    log_safe=True
                )

                y_pred = pd.DataFrame(y_pred, columns=model.classes_)

        elif task == constants.Tasks.REGRESSION:
            if is_timeseries and hasattr(model, 'forecast'):
                y_pred, X_forecast_transformed = model.forecast(X_test, y_context)

            else:
                y_pred = model.predict(X_test)

        else:
            raise NotImplementedError

        y_pred_values = y_pred.values if isinstance(y_pred, pd.DataFrame) else y_pred

        # Some pipelines will fail silently by predicting NaNs
        # E.g. a pipeline with a preprocessor that does not normalize and a linear model
        #   Pipeline[SVD, SGD] will fail if the dataset contains features on vastly different scales
        # Task to fix for ID features: 550564
        if np.issubdtype(y_pred_values.dtype, np.number):
            if np.isnan(y_pred_values).any():
                error_message = ("Silent failure occurred during prediction. "
                                 "This could be a result of unusually large values in the dataset. "
                                 "Normalizing numeric features might resolve this.")
                raise PredictionException.create_without_pii(error_message)

        # The y_pred_values (np.ndarray) is returned along with y_pred
        # to avoid potential unnecessary copies of the data from
        # calls down the line to pandas.DataFrame.values.
        return (y_pred, y_pred_values, X_forecast_transformed)
