import requests
import json


headers = {'Content-Type': 'application/x-www-form-urlencoded'}


def ret(response):
    if isinstance(response, json):
        return json.dumps(response, sort_keys=True, indent=4)
    else:
        return response


def send_get(url, params=None, headers=headers):
    response = requests.get(url=url, params=params, headers=headers)
    return ret(response)


def send_post(url, data={}, headers=headers):
    response = requests.post(url=url, data=data, headers=headers)
    return ret(response)


def send_put(url, data={}, headers=headers):
    response = requests.put(url=url, data=data, headers=headers)
    return ret(response)


def send_delete(url, data={}, headers=headers):
    response = requests.delete(url=url, data=data, headers=headers)
    return ret(response)
