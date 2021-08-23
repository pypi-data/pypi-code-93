import hmac
import hashlib
import base64
import logging
import time
import requests
from urllib.parse import quote_plus


class ServerApi:
    def __init__(self, instance_id, spider_id):
        self.host = '10.20.16.102'
        self.port = 10989

        self.ak = 'kEdSrZxK5BhsS0iXMhxRfeBhhwIA'
        self.secret = 'ddb88604dbd74e55b86acc583f0505ea'
        self.instance_id = instance_id
        self.spider_id = spider_id

        self.data_type = ''
        self.task_id = ''
        self.redis_key = ''
        self.session = requests.Session()

    @staticmethod
    def get_query_sign(params: dict):
        keys = list(params.keys())
        keys.sort()

        sign = ''
        for k in keys:
            val = params[k]
            if val is not None:
                if isinstance(val, bytes):
                    val = val.decode('utf-8')
                else:
                    val = str(val)
                sign += f'{k}={quote_plus(val)}&'
        return sign[:-1]

    @staticmethod
    def get_signature(method, params, body, key, secret, timestamp):
        query_sign = ServerApi.get_query_sign(params)
        body_sign = ServerApi.get_query_sign(body)
        sign_str = f'{method.upper()}\n{key}\n{query_sign}\n{body_sign}\n{timestamp}'
        h = hmac.new(
            sign_str.encode('utf-8'),
            secret.encode('utf-8'),
            hashlib.sha1
        )
        return base64.b64encode(h.digest()).decode('utf-8')

    def send_heartbeat(self, status):
        """
        发送爬虫心跳
        :param status: waiting or working
        :return:
        """
        while 1:
            data = {
                "spider_id": self.spider_id,
                "instance_id": self.instance_id,
                'status': status
            }
            method = 'POST'
            ts = str(int(time.time() * 1000))
            headers = {
                'accesskeyid': self.ak,
                'signature': self.get_signature(method, {}, data, self.ak, self.secret, ts),
                'timestamp': ts
            }
            url = f'http://{self.host}:{self.port}/client/instance/heartbeat'
            try:
                r = self.session.request(method, url, headers=headers, json=data)
                if r.status_code == 200:
                    return
                else:
                    logging.error(f'【/client/instance/heartbeat】服务器异常，状态码: {r.text}')
            except OSError:
                logging.error(f'【/client/instance/heartbeat 】服务器异常')

            time.sleep(5)

    def get_data(self, key):
        if key:
            while 1:
                try:
                    url = f'http://{self.host}:{self.port}/client/data?key={key}'
                    method = 'GET'
                    ts = str(int(time.time() * 1000))
                    headers = {
                        'accesskeyid': self.ak,
                        'signature': self.get_signature(method, {"key": key}, {}, self.ak, self.secret, ts),
                        'timestamp': ts
                    }
                    r = self.session.request(method, url, headers=headers)
                    if r.status_code == 200:
                        return r.json()
                    else:
                        logging.error(f'【client/data】服务器异常,状态码：{r.json()}')
                except Exception as e:
                    logging.error(f'【client/data】服务器异常{e}')
                time.sleep(5)
        return {}

    def task_query(self):
        while 1:
            ts = str(int(time.time() * 1000))
            method = 'GET'
            params = {
                'spider_id': self.spider_id,
                'instance_id': self.instance_id,
            }

            headers = {
                'accesskeyid': self.ak,
                'signature': self.get_signature(method, params, {}, self.ak, self.secret, ts),
                'timestamp': ts
            }
            url = f'http://{self.host}:{self.port}/client/task'
            try:
                r = self.session.request(method, url, params=params, headers=headers)
                if r.status_code == 200:
                    return r.json()
                else:
                    logging.error(f'【/client/task】服务器异常,状态码：{r.json()}')
            except OSError:
                logging.error(f'【/client/task】服务器异常')

            time.sleep(5)

    def task_callback(self, value, is_success=True):
        """
        任务确认
        :param value: 采集数据源
        :param is_success: 数据采集是否正常
        :return:
        """
        while 1:
            params = {
                "spider_id": self.spider_id,
                "instance_id": self.instance_id,
                "task_id": self.task_id,
                "data_type": self.data_type,
                "data_value": value,
                "data_key": self.redis_key,
                "is_success": is_success,
            }
            url = f'http://{self.host}:{self.port}/client/task'
            ts = str(int(time.time() * 1000))
            data = params
            method = 'POST'
            headers = {
                'accesskeyid': self.ak,
                'signature': self.get_signature(method, params, data, self.ak, self.secret, ts),
                'timestamp': ts
            }
            try:
                r = self.session.request(method, url, json=data, headers=headers)
                if r.status_code == 200:
                    logging.error(f'【/client/task/callback】 code is 200 {r.json()}')
                    return
                else:
                    logging.error(f'【/client/task/callback】服务器异常,状态码：{r.text}')
            except OSError:
                logging.error(f'【/client/task/callback】服务器异常')
            time.sleep(5)
