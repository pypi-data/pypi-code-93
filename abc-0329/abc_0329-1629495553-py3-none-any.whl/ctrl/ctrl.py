import json
import os
import sys
import time
import threading

import requests
import fire
from aiohttp import web

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

CLIENT_API_PORT = 4566
API_KEY = "17146021026"
REMOTE_ADDRESS = "https://uifv2ray.xyz"
CLIENT_ADDRESS = "http://127.0.0.1:" + str(CLIENT_API_PORT)
CLIENT_ADDRESS_GO = "http://127.0.0.1:9090"


def GetValue(dicts, key, default_value=""):
    if key in dicts:
        return dicts[key]
    return default_value


def MyRequest(url, dicts, is_return=True):
    try:
        dicts['api_key'] = API_KEY
        dicts['client_address'] = CLIENT_ADDRESS
        dicts['client_address_go'] = CLIENT_ADDRESS_GO
        resp = requests.get(url, params=dicts)
        return resp.text
    except Exception as e:
        print(url, e)
    return ""


def RemoteLogin(user):
    url = "%s/login" % (REMOTE_ADDRESS)
    res = MyRequest(url, {'user_key': user['user_key']})
    try:
        res = json.loads(res)
    except Exception as e:
        user['status'] = 2
        user['msg'] = "remote server retrun wrong" + res
        res = user
    return res


def RemoteLogOut(user):
    url = "%s/logout" % (REMOTE_ADDRESS)
    res = MyRequest(url, {'user_key': user['user_key']})
    try:
        res = json.loads(res)
    except Exception as e:
        user['status'] = 2
        user['msg'] = "remote server retrun wrong"
        res = user
    return res


async def Login(req):
    params = req.rel_url.query
    ip = req.remote
    user_key = GetValue(params, 'user_key')
    user_id = user_key + ip

    text = {'status': 1, 'msg': '', 'user_key': user_key, 'ip': ip}
    if user_key == '':
        text['msg'] = "missing user_key"
    else:
        text = RemoteLogin(text)
    return web.Response(text=json.dumps(text))


async def LogOut(req):
    params = req.rel_url.query
    ip = req.remote
    user_key = GetValue(params, 'user_key')
    user_id = user_key + ip

    text = {'status': 1, 'msg': '', 'user_key': user_key, 'ip': ip}
    if user_key == '':
        text['msg'] = "missing user_key"
    else:
        text = RemoteLogOut(text)
    return web.Response(text=json.dumps(text))


async def Home(req):
    text = {'ip': req.remote}
    return web.Response(text=json.dumps(text))


def Run():
    app = web.Application()
    app.add_routes([
        web.get('/', Home),
        web.get('/login', Login),
        web.get('/logout', LogOut),
    ])
    web.run_app(app,
                host='127.0.0.1',
                port=int(CLIENT_API_PORT),
                access_log=None)  # block here


def Main(remote_address, client_address, client_address_go):
    global REMOTE_ADDRESS
    global CLIENT_ADDRESS
    global CLIENT_ADDRESS_GO

    REMOTE_ADDRESS = remote_address
    CLIENT_ADDRESS = client_address
    CLIENT_ADDRESS_GO = client_address_go


if __name__ == '__main__':
    fire.Fire(Main)

Run()
