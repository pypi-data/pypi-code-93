'''
@说明    :草动开放平台基础方法
@时间    :2020/2/13 下午4:28:26
@作者    :任秋锴
@版本    :1.0
'''
import requests
from loguru import logger


class base:
    def __init__(self, token, env="api"):
        self.token = token
        self.env = env

    def request(self, api_name, data, method="GET", **kwargs):
        env_conf = {
            "dev": "apidev",
            "uat": "apiuat",
            "pre": "apipre",
            "api": "api",
        }
        host_name = f"http://{env_conf[self.env]}.icaodong.com/"
        headers = kwargs.get("headers", {})
        headers["token"] = self.token
        url = f"{host_name}{api_name}"
        response = requests.request(method=method, url=url, **kwargs)
        if method == "GET":
            response = requests.get(url, params=data, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError("网络请求方法错误。")
        if response.status_code == 200:
            return response.json()

    def response(self, response_json):
        status = response_json.get("status")
        if status == 200:
            return response_json.get("data")
        else:
            response_str = f"请求失败：{response_json}"
            raise ValueError(response_str)
