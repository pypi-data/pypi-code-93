import requests
import _d4
base_url = 'https://discord.com/api/v9'


def post(url, data):
    headers = {"Authorization": f"Bot {_d4.Token}"}
    headers["Content-Type"] = "application/json"

    response = requests.post(base_url + url, json=data, headers=headers)
    return response


def get(url, data=None):
    headers = {"Authorization": f"Bot {_d4.Token}"}
    headers["Content-Type"] = "application/json"

    response = requests.get(base_url + url, headers=headers)
    return response


def patch(url, data):
    headers = {"Authorization": f"Bot {_d4.Token}"}
    headers["Content-Type"] = "application/json"

    response = requests.patch(base_url + url, json=data, headers=headers)
    return response


def delete(url):

    headers = {"Authorization": f"Bot {_d4.Token}"}
    headers["Content-Type"] = "application/json"

    response = requests.delete(base_url + url, headers=headers)
    return response
