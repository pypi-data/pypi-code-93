import requests


def request(url, header=None, params=None, verify=None, method='get'):
    if method == 'get':
        return requests.get(url, headers=header, params=params, verify=verify)
    elif method == 'post':
        return requests.post(url, params)


def request_json(url, header=None, params=None, verify=None, method='get'):
    response = request(url, header, params, verify, method)
    return response.json()
