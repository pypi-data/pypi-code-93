from gyerpsdkcore.api.base import BaseApi
import logging
import inspect
import hashlib
import requests
import json


logger = logging.getLogger(__name__)


def _is_api_endpoint(obj):
    return isinstance(obj, BaseApi)


class BaseGyErpSdk(object):
    API_BASE_URL = 'http://v2.api.guanyierp.com/rest/erp_open'

    def __new__(cls, *args, **kwargs):
        self = super(BaseGyErpSdk, cls).__new__(cls)
        api_endpoints = inspect.getmembers(self, _is_api_endpoint)
        for name, api in api_endpoints:
            api_cls = type(api)
            api = api_cls(self)
            setattr(self, name, api)
        return self

    def __init__(self, appKey=None, sessionKey=None, secretKey=None):
        self.appKey = appKey
        self.sessionKey = sessionKey
        self.secretKey = secretKey
        self._http = requests.Session()

        assert self.appKey is not None
        assert self.sessionKey is not None
        assert self.secretKey is not None

    def _post(self, **kwargs):
        return self.post(**kwargs)

    def post(self, params):
        return self._request(http_method='post', params=params)

    def _get(self, **kwargs):
        return self.get(**kwargs)

    def get(self, params):
        return self._request(
            http_method='get',
            params=params
        )

    def _request(self, http_method, params):
        res = self._http.request(
            method=http_method,
            url=self.API_BASE_URL,
            headers={'Content-Type': 'application/json'},
            json=params
        )
        return res.json()

    def encrypt_by_MD5(self, params):
        # json转str，要注意空格，所以不能用str()直接转
        key = self.secretKey + json.dumps(params, separators=(',',':'), ensure_ascii=False) + self.secretKey
        signCode = hashlib.md5(key.encode("utf-8")).hexdigest().upper()
        return signCode

