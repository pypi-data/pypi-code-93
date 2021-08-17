# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import datetime

from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared import constants
from azureml.automl.runtime._metrics_logging import log_metrics
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.shared.metrics_utilities import compute_metrics_expr_store
from azureml.automl.runtime.shared.model_wrappers import PipelineWithYTransformations
from azureml.core import Run
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.runtime import _model_test_utilities

logger = logging.getLogger(__name__)


class ModelTestPhase:
    """AutoML job phase that evaluates the model."""

    @staticmethod
    def run(test_run: Run,
            training_run_id: str,
            dataprep_json: str,
            automl_settings: AzureAutoMLSettings) -> None:
        """
        Execute the model test run.

        :param current_run: The test run
        :param training_run_id: The id for the AutoML child run which contains the model.
        :param dataprep_json: The dataprep json which contains a reference to the test dataset.
        :param automl_settings: AzureAutoMLSettings for the parent run.
        :return:
        """
        expr_store = ExperimentStore.get_instance()
        X_test, y_test = _model_test_utilities.get_test_datasets_from_dataprep_json(dataprep_json, automl_settings)

        task = automl_settings.task_type
        fitted_model = _model_test_utilities.get_model_from_training_run(test_run.experiment, training_run_id)

        y_context = y_test if automl_settings.is_timeseries and test_run.type == 'automl.model_predictions' else None

        predict_start_time = datetime.datetime.utcnow()
        y_pred, y_pred_values, X_forecast_transformed = _model_test_utilities.inference(task,
                                                                                        fitted_model,
                                                                                        X_test,
                                                                                        y_context,
                                                                                        automl_settings.is_timeseries)
        predict_time = datetime.datetime.utcnow() - predict_start_time

        if X_forecast_transformed is not None:
            X_test = X_forecast_transformed

        if (y_test is not None) and (test_run.type == 'automl.model_test'):
            logger.info("Starting metrics computation for test run.")

            target_metrics = _model_test_utilities.get_target_metrics(task, automl_settings.is_timeseries)

            # The metrics computation for classification requires
            # the y_test values to be in encoded form.
            if task == constants.Tasks.CLASSIFICATION:
                y_transformer = expr_store.transformers.get_y_transformer()
                if y_transformer:
                    y_test = y_transformer.transform(y_test)

            if isinstance(fitted_model, PipelineWithYTransformations):
                # Pass in the underlying pipeline so that the train labels
                # retrieval inside of compute_metrics gets the encoded labels.
                fitted_model = fitted_model.pipeline

            X, y, _ = expr_store.data.materialized.get_train()
            metrics = compute_metrics_expr_store(
                X_test,
                y_test,
                X,
                y,
                y_pred_values,
                fitted_model,
                task,
                target_metrics)

            # Add predict time to scores
            metrics[constants.TrainingResultsType.PREDICT_TIME] = predict_time.total_seconds()

            log_metrics(test_run, metrics)
        else:
            logger.info("Metrics computation skipped.")

        _model_test_utilities._save_results(y_pred, test_run)
        run_lifecycle_utilities.complete_run(test_run)
