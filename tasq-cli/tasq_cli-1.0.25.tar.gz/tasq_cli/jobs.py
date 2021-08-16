import requests
import json

from tasq_cli.settings import SERVER, TOKEN
from tasq_cli import settings
from tasq_cli.server import make_request

logger = None

def run_job(project_id, tag):
    global logger
    logger = settings.get_logger()
    url = f'/jobs'
    tag = tag
    headers = {'content-type': 'application/vnd.api+json', 'accept': 'application/vnd.api+json'}

    data = {'data': {'type': 'jobs',
              'attributes': {'name': '',
                             'includeModel': False,
                             'tags': [tag],
                             'excludeTags': [],
                             'maxResources': None,
                             'forQualification': False,
                             'projectId': project_id,
                             'projectResourceIds': []}}}
    r = make_request(url, headers=headers, json=data)
    data = r.json()['data']
    del data['relationships']
    return data


def list_jobs(project_id):
    global logger
    logger = settings.get_logger()
    url = f'/jobs/?filter[project]={project_id}&sort=-id&page[size]=100'
    r = make_request(url)
    data = r.json()['data']
    for j in data:
        del(j['relationships'])
    return data


def export_job(job_id, raw, worker_data):
    global logger
    logger = settings.get_logger()
    type = 'target'
    params = '&all_judgements=false'
    if raw:
        type='raw'
    elif worker_data:
        params = '&all_judgements=true&include_worker_data=true'
    url = f'/jobs/{job_id}/download/?export_type={type}{params}'
    r = make_request(url)
    data = r.json()
    return data
