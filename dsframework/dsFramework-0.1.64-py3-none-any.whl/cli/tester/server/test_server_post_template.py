import requests
import json
from http import HTTPStatus
from pipeline.schema.inputs import generatedProjectNameInputs
from token_generator import tokenGenerator
t = tokenGenerator()
jwtToken = t.generateToken('DEFAULT_Conf')
global_headers = {
    'x-token': 'fake-super-secret-token',
    'Authorization': 'Bearer ' + jwtToken
}
base_url = 'http://localhost:8080/'

def post(endPoint, data):
    headers = {"Content-Type": "application/json; charset=UTF-8", **global_headers}
    url = base_url + endPoint
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        data = HTTPStatus.INTERNAL_SERVER_ERROR.description
    else:
        try:
            data = json.loads(response.content)
        except Exception as ex:
            data = response.content
    return data

def get(endPoint, data):
    headers = {"Content-Type": "application/json; charset=UTF-8", **global_headers}
    url = base_url + endPoint
    response = requests.get(url, params=data, headers=headers)
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        data = HTTPStatus.INTERNAL_SERVER_ERROR.description
    else:
        try:
            data = json.loads(response.content)
        except Exception as ex:
            data = response.content
    return data

if __name__ == '__main__':
    # test - parse
    data = {}
    d = generatedProjectNameInputs(**data)

    results = get('livenessprobe', {})
    print('results', results)

    results = post('parse', data)
    print('results', results)

    results = post('predict', data)
    print('results', results)

    # test - test
    batch = []
    batch.append(d.dict())
    results = post('test', batch)
    print('results', results)
