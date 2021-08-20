import os
import json

import jwt
import flask
import requests


BASE_API_URL = os.getenv('DATA_API_BASE_URL', '')
APP_SERVICE_BASE_URL = os.getenv('APP_SERVICE_BASE_URL', '')


def get_jwt_token():
    jwt_token = flask.request.cookies.get('OPSRAMP_JWT_TOKEN', '')

    return jwt_token


def get_headers():
    headers = {
        'Authorization': f'Bearer {get_jwt_token()}'
    }

    return headers


def get_msp_id():
    msp_id = None
    jwt_token = get_jwt_token()
    if jwt_token:
        decoded = jwt.decode(jwt_token, options={"verify_signature": False})
        msp_id = decoded['orgId']

    return msp_id


def call_get_requests(url, params=None, verify=True):
    headers = get_headers()
    resp = requests.get(url, headers=headers, params=params, verify=verify)

    return resp


def call_post_requests(url, params=None, data=None, verify=True):
    headers = get_headers()
    resp = requests.post(url, headers=headers, params=params, data=data, verify=verify)

    return resp


def generate_pdf(oap_name, data, size='A3', route=None):
    url = os.getenv("PDF_SERVER", '')

    post_data = {
        'report': oap_name,
        'params': json.dumps(data),
        'route': route,
        'size': size
    }

    res = requests.post(url, data=post_data).json()

    return res


def get_run_result(run_id):

    def _get_run_result(url):
        resp = requests.get(url)
        analysis_run = resp.json()

        if resp.ok and analysis_run:
            flask.session[run_id] = json.dumps(analysis_run['result'])
            result = analysis_run['result']
        else:
            result = {}
        
        return result

    if run_id:
        str_result = flask.session.get(run_id)
        if str_result:
            result = json.loads(str_result)
        else:
            url = APP_SERVICE_BASE_URL + f'/oap-api/v1/analysis-runs/{run_id}/'
            result = _get_run_result(url)
    else:
        result = {}

    return result
