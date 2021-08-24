# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods for AutoML remote runs."""
import logging
from datetime import datetime
from typing import Any

from azureml._tracing import get_tracer
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.core import Run
from azureml.train.automl.runtime._automl_job_phases import ModelTestPhase
from azureml.train.automl.utilities import _get_package_version

from azureml.train.automl.runtime._entrypoints import entrypoint_util

logger = logging.getLogger(__name__)
activity_logger = TelemetryActivityLogger()
tracer = get_tracer(__name__)


def execute(
        script_directory: str,
        automl_settings: str,
        run_id: str,
        training_run_id: str,
        dataprep_json: str,
        entry_point: str,
        **kwargs: Any
) -> None:
    """
    Compute best run or on-demand model testing in remote runs.

    :param script_directory:
    :param automl_settings:
    :param run_id: The run id for model test run.
    :param training_run_id: The id for the AutoML child run which contains the model.
    :param dataprep_json: The dataprep json which contains a reference to the test dataset.
    :param entry_point:
    :param kwargs:
    :return:
    """
    current_run = Run.get_context()

    pkg_ver = _get_package_version()
    logger.info('Using SDK version {}'.format(pkg_ver))

    try:
        print("{} - INFO - Beginning model test wrapper.".format(datetime.now().__format__('%Y-%m-%d %H:%M:%S,%f')))
        logger.info('Beginning AutoML remote driver for run {}.'.format(run_id))

        parent_run_id = entrypoint_util.get_parent_run_id(training_run_id)

        # TODO: should this last argument be training_run_id?
        automl_settings_obj = entrypoint_util.parse_settings(current_run,
                                                             automl_settings,
                                                             parent_run_id)

        # Get the post setup/featurization training data
        # which is required for metrics computation.
        cache_store = entrypoint_util.init_cache_store(current_run.experiment, parent_run_id=parent_run_id)
        expr_store = ExperimentStore(cache_store, read_only=True)
        expr_store.load()

        ModelTestPhase.run(current_run,
                           training_run_id,
                           dataprep_json,
                           automl_settings_obj)
    except Exception as e:
        logger.error("AutoML test_wrapper script terminated with an exception of type: {}".format(type(e)))
        run_lifecycle_utilities.fail_run(current_run, e)
        raise
    finally:
        ExperimentStore.reset()
