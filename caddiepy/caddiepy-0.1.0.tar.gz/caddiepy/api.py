"""
Handles all communication with the CADDIE API
"""
import requests
import json
import time
from . import settings


def drug_lookup(search_string, dataset):
    query_url = f'{settings.DOMAIN}{settings.Endpoints.DRUG_LOOKUP}'
    payload = {
        'text': search_string,
        'dataset': dataset
    }
    return requests.get(query_url, params=payload, headers=settings.HEADERS_JSON)

def map_gene_id(genes):
    query_url = f'{settings.DOMAIN}{settings.Endpoints.QUERY_NODES}'
    payload = {
        'nodes': genes,
    }
    return requests.post(query_url, data=json.dumps(payload), headers=settings.HEADERS_JSON)

def start_task(parameters):
    endpoint = f'{settings.DOMAIN}{settings.Endpoints.TASK}'
    response = requests.post(endpoint, data=parameters, headers=settings.HEADERS_JSON)
    return response.json()['token']

def get_task(token, interval=1):
    while True:
        print('Waiting for task', token)
        time.sleep(interval)
        
        endpoint_result = f'{settings.DOMAIN}{settings.Endpoints.TASK_RESULT}?token={token}'
        endpoint_task = f'{settings.DOMAIN}{settings.Endpoints.TASK}?token={token}'

        response_task = requests.get(endpoint_task).json()
        if response_task['info']['failed']:
            print(f"task {token} failed due to {response_task['info']['status']}")
            return None
        if not response_task['info']['done']:
            print(f"task {token} not yet done: {response_task['info']['status']}")
            continue

        response = requests.get(endpoint_result)
        # check here if task responded correctly
        if response.status_code != 200:
            print('Failed getting result for', token)
            continue
        print('Got results for', token)
        return response.json()

