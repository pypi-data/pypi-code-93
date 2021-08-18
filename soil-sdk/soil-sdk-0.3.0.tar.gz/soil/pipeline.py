''' This module defines a Pipeline. '''
# To prevent Pipeline not defined: https://stackoverflow.com/a/49872353/3481480
from __future__ import annotations
from time import sleep
import logging
import datetime
import copy
from typing import Optional, Dict, List, Any
from soil import api
from soil.logger import logger as soil_logger
from soil.types import Plan, ExperimentStatuses, Experiment

# How much should wait between api calls
# Remember ES takes some time to index logs
SLEEP_TIME = 1

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Pipeline:
    ''' A Pipeline stores the transformations and dependencies to obtain certain results. '''

    def __init__(self, plan: Optional[Plan] = None) -> None:
        self.plan = plan if plan is not None else []
        self.experiment: Optional[Experiment] = None
        self.finished = False

    def run(self) -> Dict[str, str]:
        ''' Run the Pipeline (blocking call until the experiment finishes) '''
        if self.finished and self.experiment:
            return self.experiment['outputs']
        if self.experiment is None:
            experiment = api.create_experiment(self.plan)
            self.experiment = experiment
        status = api.get_experiment(experiment['_id'])['experiment_status']
        start_date = datetime.datetime.now().astimezone().isoformat()
        while ExperimentStatuses(status) not in [ExperimentStatuses.DONE, ExperimentStatuses.ERROR]:
            sleep(SLEEP_TIME)
            logs = api.get_experiment_logs(experiment['_id'], start_date)
            _print_logs(logs)
            if len(logs) > 0:
                start_date = logs[0]['date']
            status = api.get_experiment(experiment['_id'])['experiment_status']
        sleep(SLEEP_TIME)
        logs = api.get_experiment_logs(experiment['_id'], start_date)
        _print_logs(logs)
        if ExperimentStatuses(status) == ExperimentStatuses.ERROR:
            raise Exception('Pipeline failed')
        logger.debug('experiment_done: %s', experiment['_id'])
        self.finished = True
        return experiment['outputs']

    def add_transformation(self, transformation: Dict[str, str]) -> Pipeline:
        '''
        Add a new transformation to the Pipeline, returns a new Pipeline
        containing the plan of the old Pipeline plus the transformation.
        '''
        new_plan = self.plan + [transformation]
        return Pipeline(plan=new_plan)

    @staticmethod
    def merge_pipelines(*pipelines: Pipeline) -> Pipeline:
        ''' Merges all the Pipelines passed into a new Pipeline that is returned. '''
        merged_plan: Plan = sum([p.plan for p in pipelines], [])
        return Pipeline(plan=merged_plan)


def _print_logs(logs: List[Dict[str, Any]]) -> None:
    for log in logs[::-1]:
        level = getattr(logging, log['level'], logging.INFO)
        nlog = copy.copy(log)
        del nlog['message']
        soil_logger.log(level, '%s - %s', nlog['date'], log['message'], extra=nlog)
