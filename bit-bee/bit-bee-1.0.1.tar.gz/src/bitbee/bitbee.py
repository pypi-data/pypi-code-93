import hashlib
import json
import random
import string
import time

import requests
from bitbee import model


class BitBeeClient(object):

    def __init__(self, env: str, corp_id: str, token: str, callback_url: str, endpoint: str) -> None:
        self.env = env
        self.corp_id = corp_id
        self.token = token
        self.callback_url = callback_url
        self.endpoint = endpoint

    def place_order(self, mobile: str, amount: str, client_order_id: str, callback_url: str = '') -> model.PlaceOrderResponse:
        nonce = self.nonce
        timestamp = str(int(time.time()))
        body = {
            'token': self.token,
            'timestamp': timestamp,
            'nonce': nonce,
            'amount': amount,
            'mobile': mobile,
            'client_order_id': client_order_id
        }
        signature = self.generate_signature(body)
        body['corp_id'] = self.corp_id
        body['signature'] = signature
        if callback_url:
            body['callback_url'] = callback_url

        data = self.__do_request('charge_std', body)
        return model.PlaceOrderResponse(
            status=data.get('status', ''),
            desc=data.get('desc', ''),
            order_id=data.get('order_id', ''),
            client_order_id=client_order_id
        )

    def query_order(self, order_id: str = '', client_order_id: str = '') -> model.QueryOrderResponse:
        if not order_id and not client_order_id:
            raise Exception('参数错误： order_id, client_order_id 不能同时为空')
        nonce = self.nonce
        timestamp = str(int(time.time()))
        body = {
            'token': self.token,
            'timestamp': timestamp,
            'nonce': nonce,
            'orderid': order_id or ''
        }
        if client_order_id:
            body['client_order_id'] = client_order_id
        signature = self.generate_signature(body)
        body['corp_id'] = self.corp_id
        body['signature'] = signature
        data = self.__do_request('queryorder_std', body)
        return model.QueryOrderResponse(
            status=data.get('status', ''),
            desc=data.get('desc', ''),
            order_id=order_id,
            client_order_id=client_order_id,
            charge_time=data.get('charge_time', ''),
            mobile=data.get('mobile', ''),
            amount=data.get('amount', '')
        )
    
    def query_balance(self) -> model.QueryBalanceResponse:
        nonce = self.nonce
        timestamp = str(int(time.time()))
        body = {
            'token': self.token,
            'timestamp': timestamp,
            'nonce': nonce
        }
        signature = self.generate_signature(body)
        body['signature'] = signature
        body['corp_id'] = self.corp_id
        data = self.__do_request('balance_std', body)
        return model.QueryBalanceResponse(
            status=data.get('status', ''),
            desc=data.get('desc', ''),
        )
    
    def query_score(self, mobile: str) -> model.QueryPointsResponse:
        nonce = self.nonce
        timestamp = str(int(time.time()))
        body = {
            'token': self.token,
            'timestamp': timestamp,
            'nonce': nonce,
            'mobile': mobile
        }
        signature = self.generate_signature(body)
        body['signature'] = signature
        body['corp_id'] = self.corp_id
        data = self.__do_request('score_std', body)
        return model.QueryPointsResponse(
            status=data.get('status', ''),
            desc=data.get('desc', '')
        )

    def __do_request(self, path: str, body: dict) -> dict:
        if self.env == 'test':
            url = f'{self.endpoint}/bitfeng_test/{path}_test/index'
        else:
            url = f'{self.endpoint}/bitfeng/{path}/index'
        print('request: %s' % url)
        resp = requests.get(url, params=body)
        return resp.json()

    def generate_signature(self, body: dict) -> str:
        return hashlib.sha1(json.dumps(body, separators=(',', ':')).encode('utf8')).hexdigest()

    @property
    def nonce(self) -> str:
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

    