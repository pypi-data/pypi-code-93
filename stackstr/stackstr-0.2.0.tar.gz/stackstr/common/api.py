from requests.auth import HTTPBasicAuth
import requests


def upload_model(api_key, model_name, model, framework):
    files = {
        'file': model
    }
    data = {
        'model_name': model_name,
        'framework': framework
    }
    resp = requests.post('https://api.stackstr.io/models', data, auth=HTTPBasicAuth(f'{api_key}', ''),
                         files=files)
    resp.raise_for_status()
    return resp
