# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict
import logging
import os

from azureml.core import Run
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru
from azureml.train.automl.runtime._many_models.many_models_train import ManyModelsTrain
from azureml.train.automl.runtime._many_models.automl_prs_driver_factory import AutoMLPRSDriverFactory
from azureml.train.automl.runtime._many_models.train_helper import Arguments
from azureml.train.automl.constants import HTSConstants
from azureml.automl.core._logging.event_logger import EventLogger
from azureml.train.automl.runtime._hts.hts_graph import Graph


logger = logging.getLogger(__name__)


class HTSAutoMLTrain(ManyModelsTrain):
    """HTS data aggregation class."""
    def __init__(
            self,
            current_step_run: Run,
            working_dir: str,
            automl_settings: Dict[str, Any],
            arguments_dict: Dict[str, str],
            event_log_dim: Dict[str, str],
            graph: Graph,
    ):
        """
        HTS data aggregation and validation run class.

        :param current_step_run: A run object that the script is running.
        :param working_dir: The working dir of the parent run.
        :param arguments_dict: The dict contains all the PRS run arguments.
        :param event_log_dim: The event log dim.
        :param graph: The hts graph.
        """
        super(HTSAutoMLTrain, self).__init__(
            current_step_run,
            automl_settings,
            process_count_per_node=int(arguments_dict.get("process_count_per_node", 10)),
            retrain_failed_models=False)

        self._console_writer.println("dir info")
        self._console_writer.println(str(os.listdir(working_dir)))
        self._console_writer.println("Current working dir is {}".format(working_dir))

        self.output_path = os.path.join(working_dir, arguments_dict[HTSConstants.OUTPUT_PATH])
        self.input_metadata = arguments_dict[HTSConstants.METADATA_INPUT]
        self.enable_engineered_explanations = hru.str_or_bool_to_boolean(
            arguments_dict[HTSConstants.ENGINEERED_EXPLANATION])
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        self.event_log_dim = event_log_dim
        self.hts_graph = graph

    def get_automl_run_prs_scenario(self):
        """Get automl PRS run scenario."""
        return AutoMLPRSDriverFactory.HTS_AUTOML_TRAIN

    def get_prs_run_arguments(self) -> Arguments:
        """Get the arguments used for the subprocess driver code."""
        return Arguments(
            process_count_per_node=self.process_count_per_node, hts_graph=self.hts_graph,
            output_path=self.output_path, input_metadata=self.input_metadata,
            engineered_explanation=self.enable_engineered_explanations,
            event_logger_dim=self.event_log_dim
        )
