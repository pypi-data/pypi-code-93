'''
This package contains calls to the SOIL's REST API
'''
import logging
from typing import Dict, Any, Optional, List
import json
from urllib.parse import urlencode
import requests
from soil.configuration import GLOBAL_CONFIG
from soil.types import Plan, GetModule, Experiment, Result

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

API_ROOT = str(GLOBAL_CONFIG.host) + '/v2/'
HEADERS = {
    'Authorization': 'Bearer ' + str(GLOBAL_CONFIG.token)
}


def upload_data(dtype: str, data: Any, metadata: Any) -> Result:
    ''' Upload data to the cloud as a new dataset.'''
    logger.debug('upload_data:%s')
    url = API_ROOT + 'results/'
    body = {
        'type': dtype,
        'data': data,
        'metadata': metadata
    }
    response = requests.post(url, headers=HEADERS, json=body)
    if response.status_code != 201:
        raise ValueError(response.text)
    return json.loads(response.text)


def get_result(result_id: str) -> Dict[str, Any]:
    ''' Get the result data '''
    logger.debug('get_result:%s', result_id)
    url = API_ROOT + 'results/' + result_id + '/'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(response.text)
    return json.loads(response.text)


def get_result_data(result_id: str, query: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    ''' Get the result data '''
    if query is None:
        query = {}
    logger.debug('get_result:%s %s', result_id, str(query))
    url = API_ROOT + 'results/' + result_id + '/data/?' + urlencode(query)
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(response.text)
    return json.loads(response.text)


def upload_module(module_name: str, code: str, is_package: bool) -> None:
    ''' Uploads a module '''
    logger.debug('upload_module:%s', module_name)
    url = API_ROOT + 'modules/'
    data = {
        'name': module_name,
        'code': code,
        'is_package': is_package
    }
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code != 200:
        raise Exception(response.text)


def get_module(full_name: str) -> GetModule:
    ''' Downloads a module '''
    logger.debug('get_module:%s', full_name)
    url = API_ROOT + 'modules/' + full_name + '/'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(response.text)
    return json.loads(response.text)


def set_alias(alias: str, result_id: str, roles: Optional[List[str]] = None) -> None:
    ''' Sets an alias for a result. Updates a previous one with the same name. '''
    logger.debug('set_alias: %s = %s', alias, result_id)
    obj = {
        'name': alias,
        'state': {
            'alias': alias,
            'result_id': result_id
        }
    }
    if roles is not None:
        obj['roles'] = roles
    try:
        old_alias_id = get_alias(alias)['_id']
        url = API_ROOT + 'states/' + old_alias_id + '/'
        response = requests.patch(url, headers=HEADERS, json=obj)
    except KeyError:
        url = API_ROOT + 'states/'
        response = requests.post(url, headers=HEADERS, json=obj)
    if response.status_code != 200:
        raise ValueError('Failed to create alias {}: {}'.format(alias, response.text))

    if roles is not None:
        url = API_ROOT + 'results/' + result_id + '/'
        response = requests.patch(url, headers=HEADERS, json={'roles': roles})
        if response.status_code != 200:
            raise ValueError('Failed to patch result {}: {}'.format(result_id, response.text))


def get_alias(alias: str) -> Dict[str, Any]:
    ''' Gets an alias '''
    logger.debug('get_alias: %s', alias)
    url = API_ROOT + 'states/?name=' + alias + '&with-roles'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise ValueError('Error getting alias:' + response.text)
    aliases = json.loads(response.text)
    if len(aliases) == 0:
        raise KeyError('Alias not found')
    alias_id = aliases[0]['_id']
    url = API_ROOT + 'states/' + alias_id + '/'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise ValueError('Error getting alias with id ' + response.text)
    return json.loads(response.text)


def create_experiment(plan: Plan) -> Experiment:
    ''' Runs an experiment in SOIL '''
    logger.debug('create_experiment: %s', str(plan))
    url = API_ROOT + 'experiments/'
    experiment = {
        'name': '',
        'description': '',
        'plan': plan
    }
    response = requests.post(url, headers=HEADERS, json={'experiment': experiment})
    if response.status_code != 200:
        raise ValueError('Error creating the experiment:' + response.text)
    return json.loads(response.text)['experiment']


def get_experiment(experiment_id: str) -> Experiment:
    ''' Runs an experiment from SOIL '''
    logger.debug('get_experiment: %s', experiment_id)
    url = API_ROOT + 'experiments/' + experiment_id + '/'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise ValueError('Error getting the experiment ' + experiment_id + '\n' + response.text)
    return json.loads(response.text)


def get_experiment_logs(experiment_id: str, start_date: str) -> Any:
    ''' Gets logs from a SOIL experiment '''
    logger.debug('get_experiment_id: %s since %s', experiment_id, start_date)
    url = API_ROOT + 'experiments/' + experiment_id + '/logs/?' + urlencode({'start_date': start_date})
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise ValueError('Error getting the experiment ' + experiment_id + '\n' + response.text)
    return json.loads(response.text)


def create_event(key: str, value: Any) -> Any:
    '''Saves an event in soil'''
    url = API_ROOT + 'alerts/events/'
    response = requests.post(url, headers=HEADERS, json={'key': key, 'value': value})
    if response.status_code != 201:
        raise ValueError('Error saving the event:' + response.text)
    return json.loads(response.text)


def create_alert(alert: Dict) -> Any:
    '''Creates an alert'''
    url = API_ROOT + 'alerts/alerts/'
    response = requests.post(url, headers=HEADERS, json=alert)
    if response.status_code != 201:
        raise ValueError('Error creating the alert:' + response.text)
    return json.loads(response.text)
