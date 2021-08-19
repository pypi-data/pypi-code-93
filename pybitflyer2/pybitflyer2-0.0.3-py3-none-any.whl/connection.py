import json
import requests
import time
import hmac
import hashlib
import urllib

from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class Authentication(requests.auth.AuthBase):
    def __init__(self, apikey, apisecret):
        self.apikey = apikey
        self.apisecret = apisecret

    def __call__(self, r):
        if not self.apikey or not self.apisecret:
            return r

        logger.debug("Using authentication")
        access_timestamp = str(time.time())
        scheme, netloc, path, query_string, fragment = urllib.parse.urlsplit(r.url)
        text = str.encode(
            access_timestamp
            + r.method
            + path
            + (f"?{query_string}" if query_string else "")
            + (r.body or "")
        )
        apisecret = str.encode(self.apisecret)
        access_sign = hmac.new(apisecret, text, hashlib.sha256).hexdigest()
        auth_header = {
            "ACCESS-KEY": self.apikey,
            "ACCESS-TIMESTAMP": access_timestamp,
            "ACCESS-SIGN": access_sign,
            "Content-Type": "application/json",
        }
        r.headers.update(auth_header)
        return r


class Connection:
    def __init__(self, apikey=None, apisecret=None) -> None:
        self.url_base = "https://api.bitflyer.jp"
        self.apikey = apikey
        self.apisecret = apisecret
        self.timeout = None

    def request(self, method, endpoint, body):
        url = urllib.parse.urljoin(self.url_base, endpoint)
        try:
            with requests.Session() as s:
                logger.debug(f"Requesting to {url}")
                if method == 'GET':
                    response = s.get(url, params=body, auth=Authentication(self.apikey, self.apisecret), timeout=self.timeout)
                elif method == 'POST':
                    response = s.post(url, auth=Authentication(self.apikey, self.apisecret), data=json.dumps(body), timeout=self.timeout)
                else:
                    raise NotImplementedError()

        except requests.RequestException as e:
            logger.warn(e)
            raise e

        content = ""
        if len(response.content) > 0:
            content = json.loads(response.content.decode("utf-8"))

        return content

    def get(self, endpoint, query):
        return self.request('GET', endpoint, query)

    def post(self, endpoint, body):
        return self.request('POST', endpoint, body)
