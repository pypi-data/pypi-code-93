import requests
import json


HEADER = {'Content-Type': 'application/json'}


def ret(response):
    if isinstance(response, dict):
        return json.dumps(response, sort_keys=True, indent=4)
    else:
        return response


def send_get(url, params=None, headers=HEADER):
    response = requests.get(url=url, params=params, headers=headers)
    return ret(response)


def send_post(url, data={}, headers=HEADER):
    response = requests.post(url=url, data=data, headers=headers)
    return ret(response)


def send_put(url, data={}, headers=HEADER):
    response = requests.put(url=url, data=data, headers=headers)
    return ret(response)


def send_delete(url, data={}, headers=HEADER):
    response = requests.delete(url=url, data=data, headers=headers)
    return ret(response)
