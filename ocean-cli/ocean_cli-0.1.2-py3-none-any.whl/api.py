import asyncio
import requests
import json
import time
import traceback
import sys
import urllib3
from urllib.parse import urljoin

from kubernetes import client, watch
from kubernetes.client.rest import ApiException

from ocean import code, utils


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def init(ctx, path, headers):
    url = urljoin(ctx.get_url(), path)

    h = {"Content-Type": "application/json", "Accept": "application/json"}
    h.update(headers)
    if ctx.get_token():
        h.update({"Authorization": "Bearer " + ctx.get_token()})

    return url, h


def handler(res):
    if res.status_code // 100 == 2:
        return res
    elif res.status_code == 401:
        print("Authentication Failed. Please run\n\n\tocean login\n")
        exit()
    else:
        body = res.json()
        if isinstance(body, dict):
            message = body.get("message")
            print(f"[{res.status_code}] {message}")
            exit()
        elif isinstance(body, list):
            for item in body:
                message = item.get("message")
                print(f"[{res.status_code}] {message}")
            exit()


def _request(method, ctx, path, data=None, headers={}):
    url, h = init(ctx, path, headers)
    try:
        res = method(url, data=json.dumps(data), headers=h)
        return handler(res)
    except Exception:
        print(f"Request Failed")
        traceback.print_exc(file=sys.stdout)
        exit()


def get(ctx, path, headers={}):
    return _request(requests.get, ctx, path, headers=headers)


def post(ctx, path, data=None, headers={}):
    return _request(requests.post, ctx, path, data=data, headers=headers)


def delete(ctx, path, data=None, headers={}):
    return _request(requests.delete, ctx, path, data=data, headers=headers)


def get_id_from_machine_type(ctx, type_name):
    res = get(ctx, "/api/users/resources")
    body = utils.dict_to_namespace(res.json())

    for mt in body.machineTypes:
        if mt.name == type_name:
            return mt.id

    return None


def get_volume_id_from_volume_name(ctx, volume_name):
    res = get(ctx, "/api/volumes")
    body = utils.dict_to_namespace(res.json())

    for vol in body.volumes:
        if vol.name == volume_name:
            return vol.volumeName

    return None
