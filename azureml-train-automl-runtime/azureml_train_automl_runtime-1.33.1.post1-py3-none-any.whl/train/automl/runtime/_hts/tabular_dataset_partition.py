# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Optional
import logging
import os
import sys

from azureml.core import Run
from azureml.automl.core.console_writer import ConsoleWriter
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru
from azureml.train.automl.constants import HTSConstants
import azureml.train.automl._hts.hts_client_utilities as cu
import azureml.train.automl.runtime._hts.hts_events as hts_events
from azureml.automl.core._logging.event_logger import EventLogger


logger = logging.getLogger(__name__)


def tabular_dataset_partition(
        arguments_dict: Dict[str, str],
        event_logger: EventLogger,
        script_run: Optional[Run] = None,
        is_inference: Optional[bool] = False
) -> None:
    """
    The driver code for hierarchy_builder step.

    :param arguments_dict: The arguments dict.
    :param is_inference: The flag to indicate whether this partition run are triggered from inference run.
    :param event_logger: The event logger.
    :param script_run: A run object that the script is running.
    :return: None
    """
    if is_inference:
        custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_DATASET_PARTITION_INF)
    else:
        custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_DATASET_PARTITION)

    if script_run is None:
        logger.info("Getting RunContext now.")
        script_run = Run.get_context()

    console_writer = ConsoleWriter(sys.stdout)

    event_logger_additional_fields = hru.get_event_logger_additional_fields(custom_dim, script_run.parent.id)
    event_logger.log_event(hts_events.PartitionTabularDatasetStart(event_logger_additional_fields))

    if is_inference:
        training_run = cu.get_training_run(arguments_dict[HTSConstants.TRAINING_RUN_ID], script_run.experiment)
        hts_run = hru.get_pipeline_run(script_run)
        hts_run.add_properties({HTSConstants.HTS_PROPERTIES_TRAINING_RUN_ID: training_run.id})

    input_dataset = script_run.input_datasets[HTSConstants.HTS_INPUT]
    local_settings_file = os.path.join(".", HTSConstants.SETTINGS_FILE)
    settings = cu.load_settings_dict_file(local_settings_file)
    output = script_run.output_datasets[HTSConstants.HTS_OUTPUT_PARTITIONED]
    partitioned_dataset_name = arguments_dict[HTSConstants.PARTITIONED_DATASET_NAME]

    datastore = script_run.experiment.workspace.get_default_datastore()
    event_logger.log_event(hts_events.PartitionTabularDatasetPartition(event_logger_additional_fields))
    partitioned_dataset = input_dataset.partition_by(
        partition_keys=cu.get_hierarchy(settings), partition_as_file_dataset=False,
        target=(datastore, partitioned_dataset_name), name=partitioned_dataset_name)
    console_writer.println("partition_keys: {}".format(partitioned_dataset.partition_keys))

    output.link(partitioned_dataset)
    script_run.add_properties({
        HTSConstants.HTS_PROPERTIES_PARTITIONED_TABULAR_DATASET_NAME: partitioned_dataset_name})
    event_logger.log_event(hts_events.PartitionTabularDatasetEnd(event_logger_additional_fields))
