''' Types used by soil library'''

from enum import Enum
from typing import List, Dict
from typing_extensions import TypedDict

Plan = List[Dict[str, str]]


class GetModule(TypedDict):
    ''' Type for GET modules/:moduleId '''
    is_package: bool
    public_api: List[str]
    package_type: str


class ExperimentStatuses(Enum):
    ''' Experiment Statuses '''
    WAITING = 'WAITING'
    EXECUTING = 'EXECUTING'
    DONE = 'DONE'
    ERROR = 'ERROR'


class Experiment(TypedDict):
    ''' Type for GET experiments/:experimentId '''
    _id: str
    app_id: str
    outputs: Dict[str, str]
    experiment_status: str


class Result(TypedDict):
    ''' Type for GET results/:resultId '''
    _id: str
    type: str
