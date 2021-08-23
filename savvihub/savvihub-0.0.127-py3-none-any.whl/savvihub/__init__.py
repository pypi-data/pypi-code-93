import os
import warnings
from typing import Dict, Any, Mapping

from savvihub.api.exceptions import APIException
from savvihub.objects import Image
from savvihub.api.savvihub import SavviHubClient
from savvihub.exceptions import ArgumentException
from savvihub.experiment import Experiment

experiment_context = None


def log(
    row: Dict[str, Any],
    step: int = None,
):
    """Log a metric during a SavviHub experiment.

    This function must be called on the SavviHub infrastructure to log the metric.
    If not executed on SavviHub's infrastructure, this function has no effect.

    :param row: a dictionary to log (required)
    :param step: a step(positive integer) for each iteration
    """
    global experiment_context
    if experiment_context is None:
        experiment_id = os.environ.get('SAVVIHUB_EXPERIMENT_ID', None)
        access_token = os.environ.get('SAVVIHUB_ACCESS_TOKEN', None)
        if experiment_id is None or access_token is None:
            return

        client = SavviHubClient(auth_header={'Authorization': f'Token {access_token}'})
        experiment_context = Experiment.from_given(experiment_id, client)
    try:
        experiment_context.log(row=row, step=step)
    except APIException as e:
        warnings.warn(f'Cannot send metrics {row} for step {step}: {e.message}')


__all__ = [
    "Image",
]