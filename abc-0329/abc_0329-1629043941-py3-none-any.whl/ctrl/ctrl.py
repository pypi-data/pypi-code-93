import json

import requests
import fire
from aiohttp import web

CLIENT_API_PORT = 4566
API_KEY = "17146021026"
REMOTE_ADDRESS = "https://uifv2ray.xyz"
MYSELF_ADDRESS = "http://127.0.0.1:4566"


def GetValue(dicts, key, default_value=""):
    if key in dicts:
        return dicts[key]
    return default_value


def MyRequest(url, dicts, is_return=True):
    try:
        dicts['api_key'] = API_KEY
        dicts['myself_address'] = MYSELF_ADDRESS
        resp = requests.get(url, params=dicts, timeout=10)
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
        user['msg'] = "remote server retrun wrong"
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


async def AddUser(req):
    params = req.rel_url.query
    ip = req.remote
    user_key = GetValue(params, 'user_key')
    api_key = GetValue(params, 'api_key')
    if api_key != API_KEY:
        return web.Response(text='wrong api_key')

    if user_key == '':
        return web.Response(text='missing user_key')

    res = MyRequest('http://127.0.0.1:9090/addUser', {'user_key': user_key})
    return web.Response(text=res)


async def RemoveUser(req):
    params = req.rel_url.query
    ip = req.remote
    user_key = GetValue(params, 'user_key')
    api_key = GetValue(params, 'api_key')
    if api_key != API_KEY:
        return web.Response(text='wrong api_key')

    if user_key == '':
        return web.Response(text='missing user_key')

    res = MyRequest('http://127.0.0.1:9090/removeUser', {'user_key': user_key})
    return web.Response(text=res)


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


async def Test(req):
    params = req.rel_url.query
    ip = req.remote
    user_key = GetValue(params, 'user_key')
    user_id = user_key + ip

    res = MyRequest('http://127.0.0.1:9090/test', {})
    text = {'caddy': '', 'ctrl': res}
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
        web.get('/add_user', AddUser),
        web.get('/test', Test),
        web.get('/remove_user', RemoveUser)
    ])
    web.run_app(app, host='127.0.0.1', port=int(CLIENT_API_PORT))  # block here


def test_main():
    MyRequest('%s/add_user' % MYSELF_ADDRESS,
              {'user_key': 'a331381d-6324-4d53-ad4f-9cda48b30648'})


def Main(remote_address, myself_address=None):
    global REMOTE_ADDRESS
    global MYSELF_ADDRESS
    REMOTE_ADDRESS = remote_address
    if myself_address is not None:
        MYSELF_ADDRESS = myself_address


if __name__ == '__main__':
    fire.Fire(Main)
else:
    test_main()

Run()
