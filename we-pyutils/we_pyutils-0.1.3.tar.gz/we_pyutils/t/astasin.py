#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : astasin.py
@Time    : 2020-02-09 7:03
@Author  : ZENKR
@Email   : zenkr@qq.com
@Software: PyCharm
@Desc    :
@license : Copyright (c) 2020 WingEase Technology Co.,Ltd. All Rights Reserved.
"""

import datetime
import json
import os

import requests
from requests_toolbelt import MultipartEncoder

DEFAULT_CLIENT_ID = os.getenv('ASTASIN_CLIENT_ID', '')
DEFAULT_CLIENT_SECRET = os.getenv('ASTASIN_CLIENT_SECRET', '')
DEFAULT_USERNAME = os.getenv('ASTASIN_USERNAME', '')
DEFAULT_PASSWORD = os.getenv('ASTASIN_PASSWORD', '')
DEFAULT_AUTH_ENDPOINT = os.getenv('ASTASIN_AUTH_ENDPOINT', 'https://weap.wingease.com')
DEFAULT_ENDPOINT = os.getenv('ASTASIN_ENDPOINT', 'https://astasin.wingease.com')


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance


class AstClient(Singleton):
    authUrl = f'{DEFAULT_AUTH_ENDPOINT}/o/token/'

    accessToken = None
    expiresIn = None
    tokenType = None
    scope = None
    refreshToken = None
    expiredAt = None

    def __init__(self, client_id=None, client_secret=None, username=None, password=None, auth_endpoint=None):
        self._client_id = client_id if client_id else DEFAULT_CLIENT_ID
        self._client_secret = client_secret if client_secret else DEFAULT_CLIENT_SECRET
        self._username = username if username else DEFAULT_USERNAME
        self._password = password if password else DEFAULT_PASSWORD
        self.auth_endpoint = auth_endpoint if auth_endpoint else DEFAULT_AUTH_ENDPOINT
        self.authUrl = f'{self.auth_endpoint}/o/token/'

    def get_token(self):
        now = datetime.datetime.now()
        if self.is_token_expired(now):
            g = self._get_token()
            if 'access_token' in g:
                self.accessToken = g['access_token']
                self.expiresIn = int(g['expires_in'])
                self.tokenType = g['token_type']
                self.scope = g['scope']
                self.refreshToken = g['refresh_token']
                self.expiredAt = now + datetime.timedelta(seconds=self.expiresIn)
            else:
                self.accessToken = None
        return self.accessToken

    def is_token_expired(self, time=None, before=30):
        if self.expiredAt is None:
            return True
        time = datetime.datetime.now() if time is None else time
        delta = (self.expiredAt - time).seconds
        if delta < before:
            return True
        return False

    def _get_token(self):
        body = {
            'grant_type': 'password',
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'username': self._username,
            'password': self._password,
        }
        m = MultipartEncoder(
            fields=body,
        )
        headers = {
            'Accept': 'application/json',
            'Content-Type': m.content_type
        }
        try:
            r = requests.post(self.authUrl, headers=headers, data=m)
            return json.loads(r.text)
        except Exception as e:
            print(e)
            return None


class AstAsin:
    url = f'{DEFAULT_ENDPOINT}/seller-product-create/'

    def __init__(self, ast_client=None, endpoint=None):
        self.endpoint = endpoint if endpoint else DEFAULT_ENDPOINT
        self.ast_client = ast_client

    def create_seller_product(self, body=None):
        url = f'{self.endpoint}/seller-product-create/'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.ast_client.get_token()}'
        }
        body = body if body else []
        try:
            r = requests.post(url, headers=headers, json=body)
            return json.loads(r.text)
        except Exception as e:
            print(e)
            return False

    def seller_country_subscription_task_get(self, results=10):
        url = f'{self.endpoint}/seller-country-subscription-task/'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.ast_client.get_token()}'
        }
        params = {
            'results': results
        }
        try:
            r = requests.get(url, headers=headers, params=params)
            return json.loads(r.text)
        except Exception as e:
            print(e)
            return False

    def seller_country_subscription_task_post(self, seller_country_subscription_id):
        url = f'{self.endpoint}/seller-country-subscription-task/'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.ast_client.get_token()}'
        }
        params = {
            'id': seller_country_subscription_id
        }
        try:
            r = requests.post(url, headers=headers, params=params)
            return json.loads(r.text)
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    import environ
    from we_pyutils.env import GetEnv

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROJECT_DIR = os.path.dirname(BASE_DIR)
    HOME_DIR = os.path.expanduser('~')
    dir_list = [
        BASE_DIR,
        PROJECT_DIR,
        HOME_DIR,
    ]

    e = GetEnv(dir_list)
    env_path = e.get_env()
    env = environ.Env()
    if env_path:
        env.read_env(env_path)
    client_id = env.str('ASTASIN_CLIENT_ID')
    client_secret = env.str('ASTASIN_CLIENT_SECRET')
    username = env.str('ASTASIN_USERNAME')
    password = env.str('ASTASIN_PASSWORD')
    auth_endpoint = env.str('ASTASIN_AUTH_ENDPOINT')
    endpoint = env.str('ASTASIN_ENDPOINT')
    client = AstClient(client_id=client_id, client_secret=client_secret, username=username,
                       password=password, auth_endpoint=auth_endpoint)
    ast_asin = AstAsin(client, endpoint)
    body = []
    body.append({
        "sellerId": 'seller_id',
        "sellerName": None,
        "asin": 'asin',
        "httpCode": 200,
        "countryCode": 'DE',
        'memo': 'TEST',
    })
    resp = ast_asin.create_seller_product(body)
    pass
