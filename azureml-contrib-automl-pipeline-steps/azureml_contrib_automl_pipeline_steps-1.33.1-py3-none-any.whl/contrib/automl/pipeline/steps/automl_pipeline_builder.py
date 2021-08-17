# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains functionality for building pipelines using AutoML for advanced model building.
"""
import json
import logging
import os
import pathlib
import shutil
import sys

from typing import Any, Dict, List, Optional, Union

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml._common._error_definition import AzureMLError
from azureml._restclient.jasmine_client import JasmineClient

from azureml.automl.core.console_writer import ConsoleWriter
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ExecutionFailure
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.core import ComputeTarget, Datastore, Environment, Experiment
from azureml.data.file_dataset import FileDataset
from azureml.data.tabular_dataset import TabularDataset
from azureml.data.output_dataset_config import OutputDatasetConfig
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.pipeline.core import PipelineData, PipelineParameter, PipelineStep
from azureml.pipeline.steps import ParallelRunConfig, ParallelRunStep
from azureml.train.automl.runtime._many_models.many_models_parameters import (
    ManyModelsTrainParameters, ManyModelsInferenceParameters
)
from azureml.train.automl.runtime._hts.hts_parameters import (
    HTSTrainParameters, HTSInferenceParameters
)

from ._assets import many_models_inference_driver, many_models_train_driver
from ._hts_pipeline_builder import _HTSPipelineBuilder
from . import utilities


MAX_AUTOML_RUN_CONCURRENCY = 320
MANY_MODELS_TRAIN_STEP_RUN_NAME = "many-models-train"
PROJECT_DIR = "automl_project_dir"
logger = logging.getLogger(__name__)


@experimental
class AutoMLPipelineBuilder:
    """
    Pipeline builder class.

    This class is used to build pipelines for AutoML training utilizing advanced modeling
    techniques including many models and hierarchical time series.
    """
    @staticmethod
    def get_many_models_train_steps(
        experiment: Experiment,
        train_data: Union[FileDataset, TabularDataset, DatasetConsumptionConfig],
        compute_target: Union[str, ComputeTarget],
        node_count: int,
        automl_settings: Optional[Dict[str, Any]] = None,
        partition_column_names: Optional[List[str]] = None,
        process_count_per_node: int = 2,
        run_invocation_timeout: int = 3700,
        train_pipeline_parameters: Optional[Union[ManyModelsTrainParameters, HTSTrainParameters]] = None,
        output_datastore: Optional[Datastore] = None,
        train_env: Optional[str] = None,
        arguments: Optional[List[Union[str, int]]] = None
    ) -> List[PipelineStep]:
        """
        Get the pipeline steps AutoML many models training.

        This method will build a list of steps to be used for training using AutoML many model scenario
        using ParallelRunStep.

        :param experiment: Experiment object.
        :param automl_settings: AutoML configuration settings to be used for triggering AutoML runs during training.
        :param train_data: The data to be used for training.
        :param compute_target: The compute target name or compute target to be used by the pipeline's steps.
        :param train_pipeline_parameters: The pipeline parameters to obtain the training pipeline.
        :param partition_column_names: Column names which are used to partition the input data.
        :param node_count: The number of nodes to be used by the pipeline steps when work is
            distributable. This should be less than or equal to the max_nodes of the compute target
            if using amlcompute.
        :param process_count_per_node: The number of processes to use per node when the work is
            distributable. This should be less than or equal to the number of cores of the
            compute target.
        :param run_invocation_timeout: Specifies timeout for each AutoML run.
        :param output_datastore: The datastore to be used for output. If specified any pipeline
            output will be written to that location. If unspecified the default datastore will be used.
        :param train_env: Specifies the environment definition to use for training. If none specified latest
            curated environment would be used.
        :param arguments: Arguments to be passed to training script.
        :returns: A list of steps which will preprocess data to the desired training_level (as set in
            the automl_settings) and train and register automl models.
        """
        jasmine_client = JasmineClient(service_context=experiment.workspace.service_context,
                                       experiment_name=experiment.name,
                                       experiment_id=experiment.id)

        if automl_settings is not None:
            AutoMLPipelineBuilder._print_deprecate_message("automl_settings", "ManyModelsParameters")
        if train_pipeline_parameters is not None:
            automl_settings = train_pipeline_parameters.automl_settings

        AutoMLPipelineBuilder._validate_max_concurrency(
            node_count, automl_settings, process_count_per_node, jasmine_client)

        if train_env is None:
            compute_name = compute_target.name if isinstance(compute_target, ComputeTarget) else compute_target
            train_env = utilities.get_step_run_env(
                automl_settings, jasmine_client, compute_target,
                experiment.workspace.compute_targets.get(compute_name).vm_size)

        if train_pipeline_parameters is not None:
            train_pipeline_parameters.validate()
        AutoMLPipelineBuilder._clean_project_dir()

        if isinstance(train_data, DatasetConsumptionConfig):
            input_dataset = train_data.dataset
            if isinstance(input_dataset, PipelineParameter):
                input_dataset = input_dataset.default_value
        else:
            input_dataset = train_data

        if isinstance(train_pipeline_parameters, HTSTrainParameters):
            # HTS does not directly support DatasetConsumptionConfig.
            return _HTSPipelineBuilder.get_hierarchy_train_steps(
                experiment, input_dataset, compute_target, node_count, train_env, process_count_per_node,
                run_invocation_timeout, output_datastore, train_pipeline_parameters.automl_settings,
                train_pipeline_parameters.enable_engineered_explanations, arguments
            )
        else:
            if partition_column_names is not None:
                AutoMLPipelineBuilder._print_deprecate_message("partition_column_names", "ManyModelsParameters")
            if train_pipeline_parameters is not None:
                partition_column_names = train_pipeline_parameters.partition_column_names

            if isinstance(train_data, FileDataset) or isinstance(train_data, TabularDataset):
                train_data = train_data.as_named_input("train_data")
            training_output_name = "many_models_training_output"

            output_dir = PipelineData(name=training_output_name,
                                      datastore=output_datastore)

            parallel_run_config = AutoMLPipelineBuilder._build_parallel_run_config_train(
                automl_settings,
                compute_target,
                node_count,
                process_count_per_node,
                run_invocation_timeout,
                partition_column_names,
                train_data,
                train_env)

            arguments = [] if arguments is None else arguments
            arguments.append("--node_count")
            arguments.append(node_count)
            parallel_run_step = ParallelRunStep(
                name=MANY_MODELS_TRAIN_STEP_RUN_NAME,
                parallel_run_config=parallel_run_config,
                allow_reuse=False,
                inputs=[train_data],
                output=output_dir,
                arguments=arguments
            )

            return [parallel_run_step]

    @staticmethod
    def get_many_models_batch_inference_steps(
        experiment: Experiment,
        inference_data: Union[FileDataset, TabularDataset, DatasetConsumptionConfig],
        compute_target: Union[str, ComputeTarget],
        node_count: int,
        process_count_per_node: int = 2,
        run_invocation_timeout: int = 3700,
        mini_batch_size=10,
        inference_pipeline_parameters: Optional[Union[HTSInferenceParameters, ManyModelsInferenceParameters]] = None,
        output_datastore: Optional[Union[Datastore, OutputDatasetConfig]] = None,
        train_run_id: Optional[str] = None,
        train_experiment_name: Optional[str] = None,
        inference_env: Optional[Environment] = None,
        time_column_name: Optional[str] = None,
        target_column_name: Optional[str] = None,
        partition_column_names: Optional[List[str]] = None,
        arguments: Optional[List[str]] = None
    ) -> List[PipelineStep]:
        """
        Get the pipeline steps AutoML many models inferencing.

        This method will build a list of steps to be used for training using AutoML many model scenario
        using ParallelRunStep.

        :param experiment: Experiment object.
        :param inference_data: The data to be used for training.
        :param compute_target: The compute target name or compute target to be used by the pipeline's steps.
        :param node_count: The number of nodes to be used by the pipeline steps when work is
            distributable. This should be less than or equal to the max_nodes of the compute target
            if using amlcompute.
        :param process_count_per_node: The number of processes to use per node when the work is
            distributable. This should be less than or equal to the number of cores of the
            compute target.
        :param run_invocation_timeout: Specifies timeout for inferencing batch.
        :param mini_batch_size: Mini batch size, indicates how many batches will be processed by one process
            on the compute.
        :param output_datastore: The datastore or outputdatasetconfig to be used for output. If specified any pipeline
            output will be written to that location. If unspecified the default datastore will be used.
        :param train_run_id: Training run id, which will be used to fetch the right environment for inferencing.
        :param train_experiment_name: Training experiment name, , which will be used to fetch the right
            environment for inferencing.
        :param inference_env: Specifies the environment definition to use for training. If none specified latest
            curated environment would be used.
        :param time_column_name: Optional parameter, used for timeseries
        :param target_column_name:  Needs to be passed only if inference data contains target column.
        :param arguments: Arguments to be passed to training script.
        :param partition_column_names: Partition column names.
        :param inference_pipeline_parameters: The pipeline parameters used for inference.
        :returns: A list of steps which will do batch inference using the inference data,
        """
        if inference_pipeline_parameters is not None:
            inference_pipeline_parameters.validate()

        if isinstance(inference_data, DatasetConsumptionConfig):
            input_dataset = inference_data.dataset
            if isinstance(input_dataset, PipelineParameter):
                input_dataset = input_dataset.default_value
        else:
            input_dataset = inference_data

        if isinstance(inference_pipeline_parameters, HTSInferenceParameters):
            return _HTSPipelineBuilder.get_hierarchy_inference_steps(
                experiment, input_dataset, inference_pipeline_parameters.hierarchy_forecast_level,
                compute_target, node_count, process_count_per_node, run_invocation_timeout,
                inference_pipeline_parameters.allocation_method, train_experiment_name,
                train_run_id, output_datastore, inference_env, arguments
            )

        if target_column_name is not None:
            AutoMLPipelineBuilder._print_deprecate_message("target_column_names", "ManyModelsParameters")
        if time_column_name is not None:
            AutoMLPipelineBuilder._print_deprecate_message("time_column_name", "ManyModelsParameters")
        if partition_column_names is not None:
            AutoMLPipelineBuilder._print_deprecate_message("partition_column_names", "ManyModelsParameters")

        if inference_pipeline_parameters is not None:
            target_column_name = inference_pipeline_parameters.target_column_name
            partition_column_names = inference_pipeline_parameters.partition_column_names
            time_column_name = inference_pipeline_parameters.time_column_name
        if inference_env is None and (train_run_id is None or train_experiment_name is None):
            raise Exception("Either pass inference_env or pass train_run_id and train_experiment_name")

        if isinstance(inference_data, FileDataset) or isinstance(inference_data, TabularDataset):
            inference_data = inference_data.as_named_input("inference_data")

        parallel_run_config = AutoMLPipelineBuilder.\
            _build_parallel_run_config_inference(experiment=experiment,
                                                 train_run_id=train_run_id,
                                                 train_experiment_name=train_experiment_name,
                                                 inference_env=inference_env,
                                                 compute_target=compute_target,
                                                 node_count=node_count,
                                                 process_count_per_node=process_count_per_node,
                                                 run_invocation_timeout=run_invocation_timeout,
                                                 mini_batch_size=mini_batch_size,
                                                 input_dataset=inference_data,
                                                 partition_column_names=partition_column_names)

        _, output_dir = utilities.get_output_datastore_and_file(output_datastore, 'many_models_inference_output')

        arguments = [] if arguments is None else arguments
        # Note that partition_column_names is reserved keyword by PRS
        arguments.append('--partition_column_names')
        arguments.extend(partition_column_names)
        if time_column_name:
            arguments.append('--time_column_name')
            arguments.append(time_column_name)
        if target_column_name:
            arguments.append('--target_column_name')
            arguments.append(target_column_name)
        parallel_run_step = ParallelRunStep(
            name="many-models-inference",
            parallel_run_config=parallel_run_config,
            inputs=[inference_data],
            output=output_dir,
            arguments=arguments,
            allow_reuse=False)
        return [parallel_run_step]

    @ staticmethod
    def _validate_max_concurrency(
            node_count: int,
            automl_settings: Dict[str, Any],
            process_count_per_node: int,
            jasmine_client: JasmineClient):
        max_concurrent_runs = node_count * process_count_per_node
        automl_settings_str = json.dumps(automl_settings)
        validation_output = jasmine_client.validate_many_models_run_input(max_concurrent_runs=max_concurrent_runs,
                                                                          automl_settings=automl_settings_str)
        validation_results = validation_output.response
        if not validation_output.is_valid and any([d.code != "UpstreamSystem"
                                                   for d in validation_results.error.details]):
            # If validation service meets error thrown by the upstream service, the run will continue.
            _console_writer = ConsoleWriter(sys.stdout)
            _console_writer.println("The validation results are as follows:")
            errors = []
            for result in validation_results.error.details:
                if result.code != "UpstreamSystem":
                    _console_writer.println(result.message)
                    errors.append(result.message)
            msg = "Validation error(s): {}".format(validation_results.error.details)
            raise ValidationException._with_error(AzureMLError.create(
                ExecutionFailure, operation_name="data/settings validation", error_details=msg))

    @ staticmethod
    def _write_automl_settings_to_file(automl_settings: Dict[str, str]):
        with open('{}//automl_settings.json'.format(PROJECT_DIR), 'w', encoding='utf-8') as f:
            json.dump(automl_settings, f, ensure_ascii=False, indent=4)

    @ staticmethod
    def _clean_project_dir():
        project_dir = pathlib.Path(PROJECT_DIR)
        if not project_dir.exists():
            project_dir.mkdir()
        else:
            try:
                files = project_dir.glob("*")
                for f in files:
                    os.remove(f)
            except Exception as e:
                _console_writer = ConsoleWriter(sys.stdout)
                _console_writer.println("Warning: Could not clean {} directory. {}".format(PROJECT_DIR, e))
                pass

    @ staticmethod
    def _build_parallel_run_config_train(
            automl_settings: Dict[str, Any],
            compute,
            node_count,
            process_count_per_node,
            run_invocation_timeout,
            partition_column_names,
            input_dataset,
            train_env: Environment):

        AutoMLPipelineBuilder._write_automl_settings_to_file(automl_settings)
        utilities._validate_run_config_train(automl_settings, compute, node_count, process_count_per_node,
                                             run_invocation_timeout, partition_column_names, input_dataset)

        # copy the driver script.
        train_driver_path = pathlib.Path(many_models_train_driver.__file__).absolute()
        shutil.copyfile(train_driver_path, os.path.join("{}/{}".format(PROJECT_DIR, train_driver_path.name)))

        if isinstance(input_dataset, DatasetConsumptionConfig):
            dataset_type = str(type(input_dataset.dataset))
        else:
            dataset_type = str(type(input_dataset))

        parallel_run_config = None
        # TODO: Merge these two in better fashion once tabular dataset is released to public.
        if(dataset_type == "<class 'azureml.data.tabular_dataset.TabularDataset'>"):
            parallel_run_config = ParallelRunConfig(
                source_directory=PROJECT_DIR,
                entry_script='many_models_train_driver.py',
                partition_keys=partition_column_names,  # do not modify this setting
                run_invocation_timeout=run_invocation_timeout,
                error_threshold=-1,
                output_action="append_row",
                environment=train_env,
                process_count_per_node=process_count_per_node,
                compute_target=compute,
                node_count=node_count)
        else:  # File dataset
            parallel_run_config = ParallelRunConfig(
                source_directory=PROJECT_DIR,
                entry_script='many_models_train_driver.py',
                mini_batch_size="1",  # do not modify this setting
                run_invocation_timeout=run_invocation_timeout,
                error_threshold=-1,
                output_action="append_row",
                environment=train_env,
                process_count_per_node=process_count_per_node,
                compute_target=compute,
                node_count=node_count)

        return parallel_run_config

    @ staticmethod
    def _build_parallel_run_config_inference(experiment,
                                             train_run_id,
                                             train_experiment_name,
                                             inference_env,
                                             compute_target,
                                             node_count,
                                             process_count_per_node,
                                             run_invocation_timeout,
                                             mini_batch_size: int,
                                             input_dataset,
                                             partition_column_names):
        # TODO: this should be user passed or get it from training run.
        if inference_env is None:
            inference_env = utilities.get_default_inference_env(
                experiment, train_run_id, train_experiment_name, MANY_MODELS_TRAIN_STEP_RUN_NAME)
        AutoMLPipelineBuilder._clean_project_dir()
        inference_driver_path = pathlib.Path(many_models_inference_driver.__file__).absolute()
        shutil.copyfile(inference_driver_path, os.path.join("{}/{}".format(PROJECT_DIR, inference_driver_path.name)))

        if isinstance(input_dataset, DatasetConsumptionConfig):
            dataset_type = str(type(input_dataset.dataset))
        else:
            dataset_type = str(type(input_dataset))

        if(dataset_type == "<class 'azureml.data.tabular_dataset.TabularDataset'>"):
            parallel_run_config = ParallelRunConfig(
                source_directory=PROJECT_DIR,
                entry_script=inference_driver_path.name,
                partition_keys=partition_column_names,
                run_invocation_timeout=run_invocation_timeout,
                error_threshold=-1,
                output_action="append_row",
                environment=inference_env,
                process_count_per_node=process_count_per_node,
                compute_target=compute_target,
                node_count=node_count)
        else:
            parallel_run_config = ParallelRunConfig(
                source_directory=PROJECT_DIR,
                entry_script=inference_driver_path.name,
                mini_batch_size='1',  # do not modify this setting
                run_invocation_timeout=run_invocation_timeout,
                error_threshold=-1,
                output_action="append_row",
                environment=inference_env,
                process_count_per_node=process_count_per_node,
                compute_target=compute_target,
                node_count=node_count)
        return parallel_run_config

    @staticmethod
    def _print_deprecate_message(old_parameter_name: str, new_parameter_name: str):
        logger.warning(
            "Parameter {} will be deprecated in the future. Please use {} instead.".format(
                old_parameter_name, new_parameter_name
            )
        )
