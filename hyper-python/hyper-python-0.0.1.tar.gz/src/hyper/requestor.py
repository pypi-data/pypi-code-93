import requests


def request(method, url, api_key, data=None):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    return requests.request(method, 'https://api.hyper.co/v6' + url, headers=headers, json=data)
