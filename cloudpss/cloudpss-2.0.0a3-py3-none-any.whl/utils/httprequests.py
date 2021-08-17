# coding=UTF-8

import json
import requests
import os
from collections import OrderedDict


def request(method, uri, baseUrl=None, params={}, token=None, **kwargs):
    if baseUrl == None:
        baseUrl = os.environ.get(
            'CLOUDPSS_API_URL', 'https://dogfood.local.cloudpss.net/')
    url = requests.compat.urljoin(baseUrl, uri)
    token = os.environ.get('CLOUDPSS_TOKEN', None)
    if token:
        headers = {'Authorization': 'Bearer ' + token,
                   'Content-Type': 'application/json; charset=utf-8'}
    else:
        raise Exception('token undefined')
    r = requests.request(method, url, params=params, headers=headers, **kwargs)
    try:
        r.raise_for_status()
    except Exception as e:
        raise Exception(r.text)
    return r
