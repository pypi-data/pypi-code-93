import os
import requests

from .. import _login

DEFAULT_REQUESTS_TIMEOUT = 90


def running_in_datalab():
    return os.environ.get('SEEQ_SDL_CONTAINER_IS_DATALAB') == 'true'


def running_in_executor():
    return os.environ.get('SEEQ_SDL_CONTAINER_IS_EXECUTOR') == 'true'


def get_label_from_executor():
    return os.environ.get('SEEQ_SDL_LABEL') or ''


def requests_get(url, params=None, timeout=DEFAULT_REQUESTS_TIMEOUT, **kwargs):
    return requests.get(url, params=params, timeout=timeout, verify=_login.https_verify_ssl, **kwargs)


def requests_patch(url, data=None, timeout=DEFAULT_REQUESTS_TIMEOUT, **kwargs):
    return requests.patch(url, data=data, timeout=timeout, verify=_login.https_verify_ssl, **kwargs)


def requests_post(url, data=None, json=None, timeout=DEFAULT_REQUESTS_TIMEOUT, **kwargs):
    return requests.post(url, data=data, json=json, timeout=timeout, verify=_login.https_verify_ssl, **kwargs)


def requests_put(url, data=None, timeout=DEFAULT_REQUESTS_TIMEOUT, **kwargs):
    return requests.put(url, data=data, timeout=timeout, verify=_login.https_verify_ssl, **kwargs)
