# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Distributed setup run."""
import json
import logging
from typing import Optional

from azureml._tracing import get_tracer
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger
from azureml.core import Run, Dataset
from azureml.train.automl.runtime._automl_job_phases import DistributedFeaturizationPhase
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext
from azureml.train.automl.runtime._entrypoints import entrypoint_util

from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.faults_verifier import VerifierManager
from azureml.automl.runtime.shared.lazy_azure_blob_cache_store import LazyAzureBlobCacheStore

logger = logging.getLogger(__name__)
activity_logger = TelemetryActivityLogger()
tracer = get_tracer(__name__)


def execute(
        script_directory: Optional[str],
        dataprep_json: str,
        automl_settings: str,
) -> None:
    setup_run = Run.get_context()
    workspace = setup_run.experiment.workspace
    try:
        verifier = VerifierManager()
        parent_run, automl_settings_obj, cache_store = entrypoint_util.init_wrapper(
            setup_run,
            automl_settings,
            script_directory
        )

        if not isinstance(cache_store, LazyAzureBlobCacheStore):
            data_store = entrypoint_util._get_cache_data_store(setup_run.experiment)
            cache_store = LazyAzureBlobCacheStore(data_store, parent_run.id)

        Contract.assert_type(value=cache_store, name='cache_store',
                             expected_types=LazyAzureBlobCacheStore)

        expr_store = ExperimentStore(cache_store, read_only=False)
        dataprep_json_obj = json.loads(dataprep_json)
        training_data_obj = dataprep_json_obj.get('training_data')
        training_dataset_id = training_data_obj['datasetId']
        validation_dataset_obj = dataprep_json_obj.get('validation_data')
        validation_dataset_id = validation_dataset_obj['datasetId']

        training_dataset = Dataset.get_by_id(workspace, training_dataset_id)
        validation_dataset = Dataset.get_by_id(workspace, validation_dataset_id)
        DistributedFeaturizationPhase.run(lambda: Run.get_context().experiment.workspace,
                                          setup_run.experiment.name,
                                          parent_run.id,
                                          automl_settings_obj,
                                          training_dataset,
                                          validation_dataset)

        parent_run_context = AzureAutoMLRunContext(parent_run)
        verifier.write_result_file(parent_run_context)
        expr_store.unload()
    except Exception as e:
        logger.error("AutoML distributed setup script terminated with an exception of type: {}".format(type(e)))
        run_lifecycle_utilities.fail_run(setup_run, e, update_run_properties=True)
        raise
    finally:
        # Reset the singleton for subsequent usage.
        ExperimentStore.reset()
