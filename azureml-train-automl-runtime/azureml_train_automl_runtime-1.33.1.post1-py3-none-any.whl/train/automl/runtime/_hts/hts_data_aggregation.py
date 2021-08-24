# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict
import pandas as pd
import os

from azureml.core import Run
from azureml.train.automl.runtime._many_models.automl_prs_run_base import AutoMLPRSRunBase
from azureml.train.automl.runtime._many_models.automl_prs_driver_factory import AutoMLPRSDriverFactory
from azureml.train.automl.runtime._many_models.train_helper import Arguments
from azureml.train.automl.constants import HTSConstants
import azureml.train.automl._hts.hts_client_utilities as cu
from azureml.train.automl.runtime._hts.hts_graph import Graph


class HTSDataAggregation(AutoMLPRSRunBase):
    """HTS data aggregation class."""
    def __init__(
            self,
            current_step_run: Run,
            working_dir: str,
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
        super(HTSDataAggregation, self).__init__(
            current_step_run,
            process_count_per_node=int(arguments_dict.get("process_count_per_node", 10)))

        self._console_writer.println("dir info")
        self._console_writer.println(str(os.listdir(working_dir)))
        self._console_writer.println("Current working dir is {}".format(working_dir))

        self.output_path = os.path.join(working_dir, arguments_dict[HTSConstants.OUTPUT_PATH])
        self.target_path = arguments_dict[HTSConstants.BLOB_PATH]
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        # Get settings
        local_settings_file = os.path.join(working_dir, HTSConstants.SETTINGS_FILE)
        self.automl_settings = cu.load_settings_dict_file(local_settings_file)

        self.event_log_dim = event_log_dim
        self.hts_graph = graph

    def get_automl_run_prs_scenario(self):
        """Get automl PRS run scenario."""
        return AutoMLPRSDriverFactory.HTS_DATA_AGGREGATION

    def get_run_result(self, output_file: str) -> pd.DataFrame:
        """Get the result of the run."""
        return pd.read_csv(output_file)

    def get_prs_run_arguments(self) -> Arguments:
        """Get the arguments used for the subprocess driver code."""
        return Arguments(
            process_count_per_node=self.process_count_per_node, hts_graph=self.hts_graph,
            output_path=self.output_path, target_path=self.target_path,
            event_logger_dim=self.event_log_dim
        )
