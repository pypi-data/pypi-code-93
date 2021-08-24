# coding:utf-8
import json

import requests


class DataClient:
    def __init__(self, base_url, token=None, **kwargs):
        self.base_url = base_url
        self.token = token
        self.kwargs = kwargs

    def request(self, method, url, params, **kwargs):
        if not kwargs.get("no_base", False):
            url = f"{self.base_url}/{url}"
        if "no_base" in kwargs:
            del kwargs["no_base"]
        real_kwargs = self.kwargs.copy()
        real_kwargs.update(kwargs)
        if self.token:
            if "headers" not in real_kwargs:
                real_kwargs["headers"] = {"Authorization": self.token}
            else:
                real_kwargs["headers"]["Authorization"] = self.token
        req = method(url, params, **real_kwargs)
        if req and req.status_code == 200:
            if len(str(req.content)) != "":
                return req.json()
            return ""
        else:
            raise Exception(f"数据获取异常：{req.text}")

    def post(self, url, params, **kwargs):
        headers = kwargs.get("headers", {})
        headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers
        if isinstance(params, str):
            params = json.loads(params)
        return self.request(requests.post, url, json.dumps(params), **kwargs)

    def get(self, url, params, **kwargs):
        if isinstance(params, str):
            params = json.loads(params)
        return self.request(requests.get, url, params, **kwargs)
