import logging

from ..api import API
from ..common import project_type_int_to_str
from ..exceptions import SABaseException

logger = logging.getLogger("superannotate-python-sdk")

_api = API.get_instance()


def search_models(
    name=None,
    type_=None,
    project_id=None,
    task=None,
    include_global=True,
):
    """Search for ML models.

    :param name: search string
    :type name: str
    :param type_: ml model type string
    :type type_: str
    :param project_id: project id
    :type project_id: str
    :param task: training task
    :type task: str
    :param include_global: include global ml models
    :type include_global: bool

    :return: ml model metadata
    :rtype: list of dicts
    """
    params = {
        "name": name,
        "team_id": _api.team_id,
        "project_id": project_id,
        "task": task,
        "type": type_,
        "include_global": include_global
    }

    response = _api.send_request(
        req_type="GET", path=f"/ml_models", params=params
    )

    if not response.ok:
        raise SABaseException(0, "could not search models")
    result = response.json()

    for model in result['data']:
        model['type'] = project_type_int_to_str(model['type'])
    if not result['data']:
        raise SABaseException(0, "Model with such a name does not exist")
    return result['data']
