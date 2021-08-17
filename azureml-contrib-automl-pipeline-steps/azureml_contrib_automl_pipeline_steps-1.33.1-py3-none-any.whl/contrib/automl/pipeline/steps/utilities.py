# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for interacting with AutoMLPipelineBuilder."""

from typing import Any, Dict, Optional, Tuple, Union

from azureml.core import ComputeTarget, Datastore, Environment, Experiment
from azureml._restclient.jasmine_client import JasmineClient
from azureml.pipeline.core import PipelineRun, PipelineData
from azureml.data.output_dataset_config import OutputDatasetConfig
from azureml.train.automl.constants import Scenarios
from .exceptions import ConflictingTimeoutException


def _validate_run_config_train(automl_settings: Dict[str, str],
                               compute,
                               node_count,
                               process_count_per_node,
                               run_invocation_timeout: int,  # in seconds
                               partition_column_names,
                               input_dataset):
    """
        Validation run config that is passed for training

        This method will validate the configuration to make sure we catch any errors before starting the run.

        :param automl_settings: AutoML configuration settings to be used for triggering AutoML runs during training.
        :param compute: The compute target name or compute target to be used by the pipeline's steps.
        :param node_count: The number of nodes to be used by the pipeline steps when work is
            distributable. This should be less than or equal to the max_nodes of the compute target
            if using amlcompute.
        :param process_count_per_node: The number of processes to use per node when the work is
            distributable. This should be less than or equal to the number of cores of the
            compute target.
        :param run_invocation_timeout: Specifies timeout for each AutoML run.
        :param partition_column_names: Column names which are used to partition the input data.
        :param input_dataset: The input dataset that is used.
    """

    experiment_timeout_hours = int(automl_settings.get('experiment_timeout_hours', 0))
    if run_invocation_timeout <= experiment_timeout_hours * 60 * 60:
        error_msg = ("run_invocation_timeout (in seconds) should be greater than experiment_timeout_hours. "
                     "The run_invocation_timeout (in seconds) should be set to maximum training time of "
                     "one AutoML run with some buffer).")
        raise ConflictingTimeoutException(error_msg)


def get_step_run_env(
        automl_settings: Dict[str, Any],
        jasmine_client: JasmineClient,
        compute: Union[str, ComputeTarget],
        compute_sku: str
) -> Environment:
    """
    Get the Environment for the pipeline steps.

    :param automl_settings: The AutoML settings dict.
    :param jasmine_client: The jasmine client to get the curated env.
    :param compute: The compute target.
    :param compute_sku: the name of the compute to be used.
    :return: The curated environment based on the dnn and gpu settings.
    """
    enable_dnn = automl_settings.get("enable_dnn", False)
    # GPU based learners are currently available only for remote runs and so not available for many model runs
    enable_gpu = automl_settings.get("enable_gpu", False)
    train_env = jasmine_client.get_curated_environment(scenario=Scenarios.AUTOML,
                                                       enable_dnn=enable_dnn,
                                                       enable_gpu=enable_gpu,
                                                       compute=compute,
                                                       compute_sku=compute_sku)

    return train_env


def get_default_inference_env(
        experiment: Experiment, train_run_id: str, train_experiment_name: str,
        step_name: str
) -> Environment:
    """Get the default inference env by giving train_run_id and train_experiment_name."""
    experiment = Experiment(experiment.workspace, train_experiment_name)
    pipeline_run = PipelineRun(experiment, train_run_id)
    step_run = pipeline_run.find_step_run(step_name)[0]
    inference_env = step_run.get_environment()
    return inference_env


def get_output_datastore_and_file(
        output: Union[OutputDatasetConfig, Datastore],
        output_name: str
) -> Tuple[Optional[Datastore], Union[OutputDatasetConfig, PipelineData]]:
    """
    Get the output datastore and the output data file location. If the input is data file,
    None will be returned as default datastore.

    :param output: The output location that will be used. It can either be a Datastore as a dir or an
        OutputDatasetConfig as a single file.
    :param output_name: The output name for the PipelineData.
    :return: A tuple that contains output Datastore and the data file.
    """
    if isinstance(output, OutputDatasetConfig):
        # if outputdatasetconfig object is passed, pass on as is to PRS
        datastore = None
        output_file = output
    else:
        datastore = output
        output_file = PipelineData(name=output_name, datastore=datastore)

    return datastore, output_file
