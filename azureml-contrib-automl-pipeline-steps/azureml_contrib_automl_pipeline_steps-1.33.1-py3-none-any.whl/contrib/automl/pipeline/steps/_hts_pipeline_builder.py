# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains functionality for building pipelines using AutoML for advanced model building.
"""
from typing import Any, Dict, List, Optional, Tuple, Union
import json
import os
from pathlib import Path
import shutil
import sys
import time

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AllowedModelsNonExplainable
from azureml.automl.core.shared.constants import _NonExplainableModels
from azureml.automl.core.shared.exceptions import ConfigException
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.core import ComputeTarget, Dataset, Datastore,\
    Experiment, Run, RunConfiguration
from azureml.core.environment import Environment
from azureml.data import LinkTabularOutputDatasetConfig, TabularDataset
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.automl.core.console_writer import ConsoleWriter
from azureml.data.file_dataset import FileDataset
from azureml.train.automl.constants import HTSConstants, HTSSupportedInputType
from azureml.train.automl._hts import hts_client_utilities
from azureml.pipeline.core import PipelineData, PipelineParameter, PipelineRun, PipelineStep
from azureml.pipeline.core._python_script_step_base import _HTSStepConstants
from azureml.pipeline.steps import ParallelRunConfig, ParallelRunStep, PythonScriptStep
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru

from . import utilities


@experimental
class _HTSPipelineBuilder(object):
    """
    Pipeline builder class.

    This class is used to build pipelines for AutoML training utilizing advanced modeling
    techniques including many models and hierarchical time series.
    """

    _ASSETS_LOCATION = "_assets"
    _PROJECT_FOLDER = "automl_pipeline_project"
    AVERAGE_HISTORICAL_PROPORTIONS = HTSConstants.AVERAGE_HISTORICAL_PROPORTIONS
    PROPORTIONS_OF_HISTORICAL_AVERAGE = HTSConstants.PROPORTIONS_OF_HISTORICAL_AVERAGE

    SCRIPT_TRAINING_DATASET_PARTITION = "partition_training_dataset_wrapper.py"
    SCRIPT_HIERARCHY_BUILDER = "hierarchy_builder_wrapper.py"
    SCRIPT_DATA_AGG = "data_aggregation_and_validation_wrapper.py"
    SCRIPT_AUTOML_TRAINING = "automl_training_wrapper.py"
    SCRIPT_PROPORTIONS_CALCULATION = "proportions_calculation_wrapper.py"
    SCRIPT_AUTOML_FORECAST_WRAPPER = "automl_forecast_wrapper.py"
    SCRIPT_INFERENCE_DATASET_PARTITION = "partition_inference_dataset_wrapper.py"
    SCRIPT_ALLOCATION_WRAPPER = "allocation_wrapper.py"
    SCRIPT_EXPLANATION_WRAPPER = "allocation_explanation_wrapper.py"

    STEP_NAME_ADDITIONAL_ARGUMENTS = {
        _HTSStepConstants.HTS_TRAINING_DATASET_PARTITION: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_HIERARCHY_BUILDER: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_DATA_AGGREGATION: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_AUTOML_TRAINING: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_PROPORTIONS: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_FORECAST: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_INFERENCE_DATASET_PARTITION: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_EXPLAIN_ALLOCATION: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_ALLOCATION: {HTSConstants.ENABLE_EVENT_LOGGER},
    }

    @staticmethod
    def get_hierarchy_train_steps(
        experiment: Experiment,
        training_data: Union[TabularDataset, FileDataset],
        compute_target: ComputeTarget,
        node_count: int,
        train_env: Environment,
        process_count_per_node: int = 2,
        run_invocation_timeout: int = 3600,
        output_datastore: Optional[Datastore] = None,
        automl_settings: Optional[Dict[str, Any]] = None,
        enable_engineered_explanations: bool = False,
        arguments: Optional[List[Union[str, int]]] = None
    ) -> List[PipelineStep]:
        """
        Get the pipeline steps hierarchical for training.

        This method will build a list of steps to be used for training hierarchical time series.
        The training uses AutoML to create and register one model per group in the hierarchy.

        :param experiment: The experiment from which the PiplineSteps will be submitted.
        :param training_data: The data to be used for training.
        :param compute_target: The compute target name or compute target to be used by the pipeline's steps.
        :param node_count: The number of nodes to be used by the pipeline steps when work is
            distributable. This should be less than or equal to the max_nodes of the compute target
            if using amlcompute.
        :param process_count_per_node: The number of processes to use per node when the work is
            distributable. This should be less than or equal to the number of cores of the
            compute target.
        :param run_invocation_timeout: The maximum time to spend on distributable portions of the run.
            If a step times out the run will not proceed.
        :param train_env: The env used for train the HTS pipeline.
        :param output_datastore: The datastore to be used for output. If specified any pipeline
            output will be written to that location. If unspecified the default datastore will be used.
        :param automl_settings: The settings to be used to construct AutoMLConfig object.
        :param enable_engineered_explanations: If True, the engineered feature explanations will be generated.
        :param arguments: The additional arguments that will be passed to each step.
        :returns: A list of steps which will preprocess data to the desired training_level (as set in
            the automl_settings) and train and register automl models.
        """
        def create_file_dataset(dataset_prefix, workspace, datastore, dataset_identifier):
            if datastore is None:
                datastore = workspace.get_default_datastore()
            blob_dir = "{}_{}".format(dataset_prefix, dataset_identifier)
            dataset_name = "{}_{}".format(dataset_prefix, dataset_identifier)

            new_dataset = Dataset.File.from_files(path=datastore.path(blob_dir + '/'), validate=False)
            registered = new_dataset.register(workspace, dataset_name, create_new_version=True)
            return blob_dir, dataset_name, registered

        # Validate that we did will not block all models if explainability is desirable.
        allowed_models = automl_settings.get('allowed_models')
        if automl_settings.get('model_explainability', True) and allowed_models is not None:
            explainable_allowed_models = set(allowed_models) - set(_NonExplainableModels.FORECASTING)
            if not explainable_allowed_models:
                raise ConfigException._with_error(
                    AzureMLError.create(AllowedModelsNonExplainable,
                                        non_explainable_models=_NonExplainableModels.FORECASTING,
                                        reference_code=ReferenceCodes._HTS_NO_EXPLAINABLE_MODELS_ALLOWED,
                                        target='allowed_models'))
        workspace = experiment.workspace

        # This will be re-enabled after JOS deploy to all regions.
        # jasmine_client = JasmineClient(service_context=experiment.workspace.service_context,
        #                                experiment_name=experiment.name,
        #                                experiment_id=experiment.id)
        # AutoMLPipelineBuilder._validate_max_concurrency(
        #     node_count, automl_settings, process_count_per_node, jasmine_client)

        os.makedirs(_HTSPipelineBuilder._PROJECT_FOLDER, exist_ok=True)
        _HTSPipelineBuilder._copy_wrapper_files(
            training_data, True, os.path.join(
                Path(os.path.abspath(__file__)).parent, _HTSPipelineBuilder._ASSETS_LOCATION))

        hts_client_utilities.validate_settings(automl_settings)
        _HTSPipelineBuilder._dump_settings(automl_settings)

        run_config = RunConfiguration()
        run_config.docker.use_docker = True
        run_config.environment = train_env

        _console_writer = ConsoleWriter(sys.stdout)

        mini_batch_size = PipelineParameter(name="batch_size_param", default_value=str(1))
        process_count_per_node = PipelineParameter(name="process_count_param", default_value=process_count_per_node)

        steps = []
        identifier = int(time.time())

        input_dataset_param = PipelineParameter(name="input-dataset", default_value=training_data)
        hierarchy_builder_output = PipelineData("hts_graph", datastore=output_datastore)

        collected_input = None
        input_dataset_type = hts_client_utilities.get_input_dataset_type(
            training_data, hts_client_utilities.get_hierarchy(automl_settings))
        if input_dataset_type == HTSSupportedInputType.FILE_DATASET:
            hb_input_partitioned_dataset = None
            data_agg_input_partition_dataset = None
            dataset_name = 'prepared_hts_training_level_data'
            prepared_hts_training_level_data = PipelineData(dataset_name, is_directory=True)
            collected_input = prepared_hts_training_level_data.as_dataset()
        elif input_dataset_type == HTSSupportedInputType.PARTITIONED_TABULAR_INPUT:
            hb_input_partitioned_dataset = training_data
            data_agg_input_partition_dataset = input_dataset_param
        elif input_dataset_type == HTSSupportedInputType.TABULAR_DATASET:
            partitioned_dataset_name = "{}_partitioned_{}".format(training_data.name, identifier)
            hb_input_partitioned_dataset = LinkTabularOutputDatasetConfig(name=HTSConstants.HTS_OUTPUT_PARTITIONED)
            data_agg_input_partition_dataset = hb_input_partitioned_dataset
            steps.append(
                _HTSPipelineBuilder._build_dataset_partition_step(
                    compute_target, run_config, training_data, hb_input_partitioned_dataset,
                    partitioned_dataset_name, is_training=True, arguments=arguments, console_writer=_console_writer))

        steps.append(
            _HTSPipelineBuilder._build_hierarchy_builder_step(
                input_dataset_type, compute_target, run_config, hierarchy_builder_output, input_dataset_param,
                collected_input, hb_input_partitioned_dataset, arguments))

        # data aggregation only support file dataset and tabular dataset with partitions
        agg_metadata = PipelineData("data_aggregation_and_validation", datastore=output_datastore)
        agg_blob_dir, agg_dataset_name, agg_file_dataset = create_file_dataset(
            "hts_agg", workspace, output_datastore, identifier)
        _console_writer.println("Aggregation dataset is created with the name {}".format(agg_dataset_name))

        steps.append(
            _HTSPipelineBuilder._build_data_agg_step(
                input_dataset_type, compute_target, mini_batch_size, automl_settings, process_count_per_node,
                run_invocation_timeout, node_count, agg_metadata, agg_blob_dir, hierarchy_builder_output,
                train_env, collected_input, data_agg_input_partition_dataset, arguments))

        training_metadata = PipelineData("automl_training", datastore=output_datastore)
        automl_train_arguments = [
            HTSConstants.OUTPUT_PATH, training_metadata,
            HTSConstants.METADATA_INPUT, agg_metadata,
            HTSConstants.HTS_GRAPH, hierarchy_builder_output,
            HTSConstants.ENGINEERED_EXPLANATION, enable_engineered_explanations,
            HTSConstants.NODES_COUNT, node_count]
        automl_train_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            _HTSStepConstants.HTS_AUTOML_TRAINING, arguments
        ))
        automl_train_parallel_run_config = ParallelRunConfig(
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            entry_script=_HTSPipelineBuilder.SCRIPT_AUTOML_TRAINING,
            mini_batch_size=mini_batch_size,
            error_threshold=-1,
            output_action="append_row",
            append_row_file_name="outputs.txt",
            compute_target=compute_target,
            environment=train_env,
            process_count_per_node=process_count_per_node,
            run_invocation_timeout=run_invocation_timeout,
            node_count=node_count)

        automl_train_prs = ParallelRunStep(
            name=_HTSStepConstants.HTS_AUTOML_TRAINING,
            parallel_run_config=automl_train_parallel_run_config,
            arguments=automl_train_arguments,
            inputs=[agg_file_dataset.as_named_input('aggregated_hierarchy_level_data')],
            output=training_metadata,
            side_inputs=[agg_metadata, hierarchy_builder_output],
            allow_reuse=False
        )
        steps.append(automl_train_prs)

        proportions_calculation = PipelineData("proportions_calculation", datastore=output_datastore)
        prop_calc_arguments = [
            HTSConstants.METADATA_INPUT, training_metadata,
            HTSConstants.HTS_GRAPH, hierarchy_builder_output]
        prop_calc_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            _HTSStepConstants.HTS_PROPORTIONS, arguments
        ))
        prop_calc_pss = PythonScriptStep(
            name=_HTSStepConstants.HTS_PROPORTIONS,
            script_name=_HTSPipelineBuilder.SCRIPT_PROPORTIONS_CALCULATION,
            compute_target=compute_target,
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            inputs=[training_metadata, hierarchy_builder_output],
            arguments=prop_calc_arguments,
            outputs=[proportions_calculation],
            runconfig=run_config,
            allow_reuse=False
        )

        steps.append(prop_calc_pss)

        if automl_settings.get('model_explainability', True):
            steps.append(_HTSPipelineBuilder._build_explain_allocation_step(
                training_metadata,
                hierarchy_builder_output,
                compute_target=compute_target,
                runconfig=run_config,
                output_datastore=output_datastore,
                training_datastore=output_datastore,
                enable_engineered_explanations=enable_engineered_explanations))

        return steps

    @staticmethod
    def get_hierarchy_inference_steps(
        experiment: Experiment,
        inference_data: Union[TabularDataset, FileDataset],
        hierarchy_forecast_level: str,
        compute_target: Union[str, ComputeTarget],
        node_count: int,
        process_count_per_node: int = 2,
        run_invocation_timeout: int = 600,
        allocation_method: str = PROPORTIONS_OF_HISTORICAL_AVERAGE,
        train_experiment_name: Optional[str] = None,
        training_run_id: Optional[str] = None,
        output_datastore: Optional[Datastore] = None,
        inference_env: Optional[Environment] = None,
        arguments: Optional[List[Union[str, int]]] = None
    ) -> List[PipelineStep]:
        """
        Get the pipeline steps hierarchical for inferencing.

        This method should be used in conjunction with get_hierarchy_training_steps. This method
        will build an inference pipeline which can be used to coherently allocate forecasts
        from models trained through automl hierarchical time series training pipelines.

        :param experiment: The inference experiment.
        :param training_run_id: The pipeline run id which was used to train automl models. If this parameter is None.
            the latest successful training run will be used.
        :param train_experiment_name: The experiment name which the training_run lives.
        :param inference_data: The data to be used for inferencing.
        :param hierarchy_forecast_level: The default level to be used for inferencing. The pipeline
            will first aggregate data to the selected training level and then allocate forecasts to
            the desired forecast level. This can be modified on the pipeline through the
            PipelineParameter of the same name.
        :param allocation_method: The allocation method to be used for inferencing. This method will be
            used if the hierarchy_forecast_level is different from the training_level. This can be
            modified through the PipelineParameter of the same name.
        :param compute_target: The compute target name or compute target to be used by the pipeline's steps.
        :param node_count: The number of nodes to be used by the pipeline steps when work is
            distributable. This should be less than or equal to the max_nodes of the compute target
            if using amlcompute.
        :param process_count_per_node: The number of processes to use per node when the work is
            distributable. This should be less than or equal to the number of cores of the
            compute target.
        :param run_invocation_timeout: The maximum time to spend on distributable portions of the run.
            If a step times out the run will not proceed.
        :param output_datastore: The datastore to be used for output. If specified any pipeline
            output will be written to that location. If unspecified the default datastore will be used.
        :param inference_env: The inference environment.
        :param arguments: The additional arguments that will be passed to each step.
        :returns: A list of steps which will preprocess data to the desired training_level (as set in
            the automl_settings) and train and register automl models.
        """
        os.makedirs(_HTSPipelineBuilder._PROJECT_FOLDER, exist_ok=True)

        root_path = Path(os.path.abspath(__file__)).parent
        path_to_assets = os.path.join(root_path, _HTSPipelineBuilder._ASSETS_LOCATION)
        _HTSPipelineBuilder._copy_wrapper_files(inference_data, False, path_to_assets)
        _console_writer = ConsoleWriter(sys.stdout)

        if train_experiment_name is None:
            training_experiment = experiment
            train_experiment_name = experiment.name
        else:
            training_experiment = Experiment(experiment.workspace, train_experiment_name)

        if training_run_id is None:
            training_run = hts_client_utilities.get_latest_successful_training_run(training_experiment)
            training_run_id = training_run.id
            _console_writer.println("The training run used for inference is {}.".format(training_run_id))
        else:
            training_run = PipelineRun(training_experiment, training_run_id)

        if inference_env is None:
            inference_env = utilities.get_default_inference_env(
                experiment, training_run_id, train_experiment_name, _HTSStepConstants.HTS_AUTOML_TRAINING
            )

        run_config = RunConfiguration()
        run_config.docker.use_docker = True
        run_config.environment = inference_env

        forecast_param = PipelineParameter(name="hierarchy_forecast_level", default_value=hierarchy_forecast_level)
        allocation_param = PipelineParameter(name="allocation_method", default_value=allocation_method)
        input_dataset_param = PipelineParameter(name="input-dataset", default_value=inference_data)

        steps = []

        settings = json.loads(training_run.properties[HTSConstants.HTS_PROPERTIES_SETTINGS])
        _HTSPipelineBuilder._dump_settings(settings)
        partition_keys = hts_client_utilities.get_hierarchy_to_training_level(settings)
        input_dataset_type = hts_client_utilities.get_input_dataset_type(inference_data, partition_keys)
        if input_dataset_type == HTSSupportedInputType.TABULAR_DATASET:
            identifier = int(time.time())
            partitioned_dataset_name = "{}_partitioned_{}".format(inference_data.name, identifier)
            fp_input_partitioned_dataset = LinkTabularOutputDatasetConfig(name=HTSConstants.HTS_OUTPUT_PARTITIONED)
            steps.append(
                _HTSPipelineBuilder._build_dataset_partition_step(
                    compute_target, run_config, inference_data, fp_input_partitioned_dataset,
                    partitioned_dataset_name, is_training=False, training_run_id=training_run_id,
                    console_writer=_console_writer))
        elif input_dataset_type == HTSSupportedInputType.PARTITIONED_TABULAR_INPUT:
            fp_input_partitioned_dataset = input_dataset_param
        elif input_dataset_type == HTSSupportedInputType.FILE_DATASET:
            fp_input_partitioned_dataset = None

        datastore, output_allocations = utilities.get_output_datastore_and_file(
            output_datastore, "allocated_forecasts")
        output_forecasts = PipelineData(
            name="raw_forecasts", datastore=datastore, pipeline_output_name="forecasts")

        steps.append(
            _HTSPipelineBuilder._build_forecast_parallel_step(
                input_dataset_type, input_dataset_param, inference_env, compute_target, node_count,
                process_count_per_node,
                run_invocation_timeout, training_run_id, output_forecasts,
                fp_input_partitioned_dataset, partition_keys))

        inf_allocation = PythonScriptStep(
            name=_HTSStepConstants.HTS_ALLOCATION,
            script_name=_HTSPipelineBuilder.SCRIPT_ALLOCATION_WRAPPER,
            inputs=[output_forecasts.as_mount()],
            outputs=[output_allocations],
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            arguments=[
                HTSConstants.TRAINING_RUN_ID, training_run_id,
                HTSConstants.OUTPUT_PATH, output_allocations,
                HTSConstants.ALLOCATION_METHOD, allocation_param,
                HTSConstants.FORECAST_LEVEL, forecast_param,
                HTSConstants.RAW_FORECASTS, output_forecasts,
            ],
            runconfig=run_config,
            compute_target=compute_target,
            allow_reuse=False
        )
        steps.append(inf_allocation)

        return steps

    @staticmethod
    def get_training_step(pipeline_run: PipelineRun) -> Optional[Run]:
        """
        Get the AutoML training step.

        This can be used to get the automl training step to check how many groups
        are left to train. A link to the step will also be printed. If the step is
        not found, None will be returned.

        :param pipeline_run: The PipelineRun object containing an automl training step.
        """
        _console_writer = ConsoleWriter(sys.stdout)
        step_list = pipeline_run.find_step_run("automl-training")
        if not step_list:
            _console_writer.println(
                "No AutoML Training run found. This could be because the pipeline has not started training.")
            return None
        at = step_list[0]
        _console_writer.println("View the AutoML training run here: {}".format(at.get_portal_url()))
        return at

    @staticmethod
    def get_training_step_status(pipeline_run: PipelineRun) -> Tuple[Optional[int], Optional[int]]:
        """
        Get the number of AutoML Training jobs remaining on the run.

        Returns a tuple of reminaing_items, total_items. If the AutoML training step is not found,
        None, None is returned. If there is a problem getting remaning job count or total job
        count None will be returned for the respective number.

        :param pipeline_run: The PipelineRun object containing the automl training step.
        """
        _console_writer = ConsoleWriter(sys.stdout)
        at = _HTSPipelineBuilder.get_training_step(pipeline_run)
        if at is None:
            return None, None
        remaining_items_list = at.get_metrics("Remaining Items").get("Remaining Items", [])
        total_items = at.get_metrics("Total MiniBatches").get("Total MiniBatches")
        if not remaining_items_list:
            _console_writer.println("Could not retrieve remaining items.")
            remaining_items = None
        else:
            remaining_items = remaining_items_list[-1]

        if not total_items:
            _console_writer.println("Could not retrieve total items.")

        if total_items and remaining_items:
            _console_writer.println("{} out of {} jobs remaining".format(remaining_items, total_items))

        return remaining_items, total_items

    @staticmethod
    def _copy_wrapper_files(dataset: Dataset, is_training: bool, path_to_assets: str) -> None:
        """Copy the wrapper file according to dataset type and run type"""
        if is_training:
            if hts_client_utilities.is_file_dataset(dataset):
                files_to_copy = [_HTSPipelineBuilder.SCRIPT_HIERARCHY_BUILDER]
            else:
                files_to_copy = [
                    _HTSPipelineBuilder.SCRIPT_TRAINING_DATASET_PARTITION,
                    _HTSPipelineBuilder.SCRIPT_HIERARCHY_BUILDER]
            files_to_copy.append(_HTSPipelineBuilder.SCRIPT_DATA_AGG)
            files_to_copy.append(_HTSPipelineBuilder.SCRIPT_AUTOML_TRAINING)
            files_to_copy.append(_HTSPipelineBuilder.SCRIPT_PROPORTIONS_CALCULATION)
            files_to_copy.append(_HTSPipelineBuilder.SCRIPT_EXPLANATION_WRAPPER)
        else:
            if hts_client_utilities.is_file_dataset(dataset):
                files_to_copy = []
            else:
                files_to_copy = [_HTSPipelineBuilder.SCRIPT_INFERENCE_DATASET_PARTITION]
            files_to_copy.append(_HTSPipelineBuilder.SCRIPT_AUTOML_FORECAST_WRAPPER)
            files_to_copy.append(_HTSPipelineBuilder.SCRIPT_ALLOCATION_WRAPPER)

        for f in files_to_copy:
            shutil.copy(os.path.join(path_to_assets, f), _HTSPipelineBuilder._PROJECT_FOLDER)

    @staticmethod
    def _build_dataset_partition_step(
            compute_target: Union[str, ComputeTarget],
            run_config: RunConfiguration,
            input_dataset: Dataset,
            link_partition_output_config: LinkTabularOutputDatasetConfig,
            partitioned_dataset_name: str,
            is_training: bool,
            console_writer: ConsoleWriter,
            training_run_id: Optional[str] = HTSConstants.DEFAULT_ARG_VALUE,
            arguments: Optional[List[Union[str, int]]] = None
    ) -> PythonScriptStep:
        """Build dataset partition step."""
        if is_training:
            step_name = _HTSStepConstants.HTS_TRAINING_DATASET_PARTITION
            script_name = _HTSPipelineBuilder.SCRIPT_TRAINING_DATASET_PARTITION
            pipeline_type = "training"
        else:
            step_name = _HTSStepConstants.HTS_INFERENCE_DATASET_PARTITION
            script_name = _HTSPipelineBuilder.SCRIPT_INFERENCE_DATASET_PARTITION
            pipeline_type = "inference"
        console_writer.println(
            "A partitioned tabular dataset will be created with the name {} after {}. "
            "You may use it for future {}.".format(pipeline_type, partitioned_dataset_name, pipeline_type))
        step_arguments = [
            HTSConstants.PARTITIONED_DATASET_NAME, partitioned_dataset_name,
            HTSConstants.TRAINING_RUN_ID, training_run_id]
        step_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            step_name, arguments
        ))
        partition_step = PythonScriptStep(
            name=step_name,
            script_name=script_name,
            compute_target=compute_target,
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            inputs=[input_dataset.as_named_input(HTSConstants.HTS_INPUT)],
            outputs=[link_partition_output_config],
            arguments=step_arguments,
            runconfig=run_config,
            allow_reuse=False
        )
        return partition_step

    @staticmethod
    def _build_hierarchy_builder_step(
            training_data_type: HTSSupportedInputType,
            compute_target: Union[str, ComputeTarget],
            run_config: RunConfiguration,
            hierarchy_builder_output: str,
            input_dataset_param: Optional[PipelineParameter] = None,
            collected_input: Optional[str] = None,
            input_partitioned_dataset: Optional[Union[LinkTabularOutputDatasetConfig, TabularDataset]] = None,
            arguments: Optional[List[Union[str, int]]] = None
    ) -> PythonScriptStep:
        """Build hierarchy builder step."""
        if training_data_type == HTSSupportedInputType.FILE_DATASET:
            mounted_consumption_config = DatasetConsumptionConfig(
                HTSConstants.HTS_INPUT, input_dataset_param).as_mount()
            inputs = [mounted_consumption_config]
            step_arguments = [
                HTSConstants.INPUT_DATASET, mounted_consumption_config,
                HTSConstants.OUTPUT_PATH, hierarchy_builder_output,
                HTSConstants.BLOB_PATH, collected_input
            ]
            outputs = [collected_input, hierarchy_builder_output]
        else:
            if training_data_type == HTSSupportedInputType.PARTITIONED_TABULAR_INPUT:
                inputs = [input_partitioned_dataset.as_named_input(HTSConstants.HTS_INPUT), ]
            else:
                inputs = [input_partitioned_dataset.as_input(HTSConstants.HTS_INPUT), ]
            step_arguments = [
                HTSConstants.OUTPUT_PATH, hierarchy_builder_output,
                HTSConstants.INPUT_DATASET, HTSConstants.DEFAULT_ARG_VALUE,
                HTSConstants.BLOB_PATH, HTSConstants.DEFAULT_ARG_VALUE,
            ]
            outputs = [hierarchy_builder_output, ]

        step_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            _HTSStepConstants.HTS_HIERARCHY_BUILDER, arguments
        ))

        hierarchy_builder_step = PythonScriptStep(
            name=_HTSStepConstants.HTS_HIERARCHY_BUILDER,
            script_name=_HTSPipelineBuilder.SCRIPT_HIERARCHY_BUILDER,
            compute_target=compute_target,
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            inputs=inputs,
            arguments=step_arguments,
            outputs=outputs,
            runconfig=run_config,
            allow_reuse=False
        )

        return hierarchy_builder_step

    @staticmethod
    def _build_data_agg_step(
            training_data_type: HTSSupportedInputType,
            compute_target: Union[str, ComputeTarget],
            mini_batch_size: PipelineParameter,
            automl_settings: Dict[str, Any],
            process_count_per_node: PipelineParameter,
            run_invocation_timeout: int,
            node_count: int,
            agg_metadata: str,
            agg_blob_dir: str,
            hierarchy_builder_output: str,
            train_env: Environment,
            collected_input: Optional[str] = None,
            partitioned_tabular_dataset: Optional[
                Union[LinkTabularOutputDatasetConfig, PipelineParameter]] = None,
            arguments: Optional[List[Union[str, int]]] = None
    ) -> ParallelRunStep:
        """Build data aggregation step."""
        if training_data_type == HTSSupportedInputType.FILE_DATASET:
            error_threshold = 10
            partition_keys = None
            inputs = [collected_input.as_named_input('hierarchy_level_input_data'), ]
        else:
            error_threshold = -1
            partition_keys = hts_client_utilities.get_hierarchy_to_training_level(automl_settings)
            if training_data_type == HTSSupportedInputType.TABULAR_DATASET:
                inputs = [partitioned_tabular_dataset, ]
            else:
                inputs = [DatasetConsumptionConfig(HTSConstants.HTS_INPUT, partitioned_tabular_dataset)]
            mini_batch_size = None

        agg_data_parallel_run_config = ParallelRunConfig(
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            entry_script=_HTSPipelineBuilder.SCRIPT_DATA_AGG,
            mini_batch_size=mini_batch_size,
            error_threshold=error_threshold,
            output_action="append_row",
            append_row_file_name="outputs.txt",
            compute_target=compute_target,
            environment=train_env,
            process_count_per_node=process_count_per_node,
            run_invocation_timeout=run_invocation_timeout,
            node_count=node_count,
            partition_keys=partition_keys)

        step_arguments = [HTSConstants.OUTPUT_PATH, agg_metadata,
                          HTSConstants.BLOB_PATH, agg_blob_dir,
                          HTSConstants.HTS_GRAPH, hierarchy_builder_output,
                          HTSConstants.NODES_COUNT, node_count]
        step_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            _HTSStepConstants.HTS_DATA_AGGREGATION, arguments
        ))

        agg_data_prs = ParallelRunStep(
            name=_HTSStepConstants.HTS_DATA_AGGREGATION,
            parallel_run_config=agg_data_parallel_run_config,
            arguments=step_arguments,
            inputs=inputs,
            output=agg_metadata,
            side_inputs=[hierarchy_builder_output],
            allow_reuse=False
        )

        return agg_data_prs

    @staticmethod
    def _build_forecast_parallel_step(
            input_dataset_type: HTSSupportedInputType,
            input_dataset_param: PipelineParameter,
            environment: Experiment,
            compute_target: Union[str, ComputeTarget],
            node_count: int,
            process_count_per_node: PipelineParameter,
            run_invocation_timeout: int,
            training_run_id: str,
            output_forecasts: str,
            input_partitioned_dataset: Union[TabularDataset, PipelineParameter] = None,
            partition_keys: Optional[str] = None,
            arguments: Optional[List[Union[str, int]]] = None
    ) -> ParallelRunStep:
        """Build forecast parallel step."""
        if input_dataset_type == HTSSupportedInputType.FILE_DATASET:
            mounted_consumption_config = DatasetConsumptionConfig(
                HTSConstants.HTS_INPUT, input_dataset_param).as_mount()
            inputs = [mounted_consumption_config]
            mini_batch_size = 1
            partition_keys = None
        else:
            if input_dataset_type == HTSSupportedInputType.TABULAR_DATASET:
                inputs = [input_partitioned_dataset, ]
            else:
                inputs = [DatasetConsumptionConfig(HTSConstants.HTS_INPUT, input_partitioned_dataset)]
            mini_batch_size = None

        inf_prc = ParallelRunConfig(
            environment=environment,
            entry_script=_HTSPipelineBuilder.SCRIPT_AUTOML_FORECAST_WRAPPER,
            error_threshold=-1,
            output_action="append_row",
            append_row_file_name=HTSConstants.HTS_FILE_RAW_PREDICTIONS,
            compute_target=compute_target,
            node_count=node_count,
            process_count_per_node=process_count_per_node,
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            description="forecast-parallel-config",
            run_invocation_timeout=run_invocation_timeout,
            run_max_try=3,
            mini_batch_size=mini_batch_size,
            partition_keys=partition_keys
        )

        step_arguments = [
            HTSConstants.TRAINING_RUN_ID, training_run_id,
            HTSConstants.OUTPUT_PATH, output_forecasts,
            HTSConstants.APPEND_HEADER_PRS, True,
            HTSConstants.NODES_COUNT, node_count,
        ]
        step_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            _HTSStepConstants.HTS_FORECAST, arguments
        ))

        inf_prs = ParallelRunStep(
            name=_HTSStepConstants.HTS_FORECAST,
            inputs=inputs,
            arguments=step_arguments,
            output=output_forecasts,
            parallel_run_config=inf_prc,
            allow_reuse=False
        )

        return inf_prs

    @staticmethod
    def _build_explain_allocation_step(
            training_metadata: PipelineData,
            hierarchy_builder_output: PipelineData,
            compute_target: Union[str, ComputeTarget],
            runconfig: RunConfiguration,
            output_datastore: Dataset,
            training_datastore: Dataset,
            enable_engineered_explanations: bool,
            arguments: Optional[List[Union[str, int]]] = None
    ) -> PythonScriptStep:
        """
        Build The step for allocation of explanations.

        :param training_metadata: The metadata obtained from the training step.
        :param compute_target: The compute target to be used for allocation.
        :param output_datastore: The data store used to output the explanations.
        :param training_datastore: The data store used by a training step.
        :return: The explanation step.
        """
        output_explanations = PipelineData(
            name=HTSConstants.HTS_EXPLANATIONS_OUT,
            datastore=output_datastore,
            pipeline_output_name=HTSConstants.HTS_DIR_EXPLANATIONS)

        step_arguments = [
            HTSConstants.EXPLANATION_DIR, training_metadata,
            HTSConstants.HTS_GRAPH, hierarchy_builder_output,
            HTSConstants.ENGINEERED_EXPLANATION, enable_engineered_explanations,
            HTSConstants.OUTPUT_PATH, output_explanations,
        ]
        step_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            _HTSStepConstants.HTS_EXPLAIN_ALLOCATION, arguments
        ))

        return PythonScriptStep(
            name=_HTSStepConstants.HTS_EXPLAIN_ALLOCATION,
            script_name=_HTSPipelineBuilder.SCRIPT_EXPLANATION_WRAPPER,
            outputs=[output_explanations],
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            inputs=[training_metadata, hierarchy_builder_output],
            arguments=step_arguments,
            compute_target=compute_target,
            runconfig=runconfig,
            allow_reuse=False
        )

    @staticmethod
    def _dump_settings(automl_settings: Dict[str, Any]) -> None:
        """Dump the settings to a json file in the project folder."""
        settings_path = os.path.join(_HTSPipelineBuilder._PROJECT_FOLDER, HTSConstants.SETTINGS_FILE)
        hru.dump_object_to_json(automl_settings, settings_path)

    @staticmethod
    def _get_additional_step_arguments(
            step_name: str, arguments: Optional[List[Union[str, int]]] = None
    ) -> List[Union[str, int]]:
        """Get additional step arguments from input arguments."""
        filtered_args = []
        if not arguments:
            return filtered_args

        for i, arg in enumerate(arguments):
            if arg in _HTSPipelineBuilder.STEP_NAME_ADDITIONAL_ARGUMENTS[step_name]:
                if i < len(arguments) - 1:
                    filtered_args.append(arg)
                    filtered_args.append(arguments[i + 1])
                else:
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            ArgumentBlankOrEmpty,
                            argument_name=arg,
                            reference_code=ReferenceCodes._HTS_NO_ARGUMENT_PROVIDED,
                            target='arguments'))

        return filtered_args
