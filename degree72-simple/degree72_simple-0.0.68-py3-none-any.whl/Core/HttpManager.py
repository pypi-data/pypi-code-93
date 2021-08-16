import requests
import re
import urllib3

urllib3.disable_warnings()
import os

if os.name == "nt":  # windows
    from urllib3.exceptions import InsecureRequestWarning

    urllib3.disable_warnings(InsecureRequestWarning)


class HttpManager:
    _headers = {}

    def __init__(self
                 , proxy
                 , max_hourly_page_view
                 , default_header
                 , log
                 , timeout):
        self.log = log
        self.proxy = proxy

        self._maxHourlyPageView = int(max_hourly_page_view)
        self.out_time = timeout

        # Take notes for every request for every url
        self.retry_times = dict()
        # self._requestTimeOut = timeout
        # self._traffic = 0
        # self._trafficInterval = 100
        # self._lastPoolIndex = 0
        # self._carrier = carrier
        # self._API_Interval = 30

        self.encoding = None

        self._headers = dict()
        self._cookies = dict()

        if default_header:
            self._init_header()

    def set_header(self, key, val):
        key = re.sub(r'//\d', '', key)
        self._headers[key] = val

    def set_cookie(self, cookies):
        self._cookies = cookies

    def download_page(self, url, **kwargs):
        try:
            post_data = kwargs.get("post_data")
            if post_data:  # post
                resp = self.http_post(url, post_data=post_data)
            else:  # get
                resp = self.http_get(url)

            if resp is None or resp.status_code != 200:
                self.log.warn("response error. ", str(resp.status_code))
            return resp

        except Exception as e:
            self.log.warn("Exception DownloadPage"
                          , "url: [%s] mes: [%s]" % (url, str(e)))

    def _init_header(self):
        self.set_header("Proxy-Connection",
                        "keep-alive")
        self.set_header("User-Agent",
                        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36")
        self.set_header("Accept",
                        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8")
        self.set_header("Accept-Language",
                        "en-US")
        self.set_header("Accept-Encoding",
                        "gzip, deflate")
        self.set_header("Content-Type",
                        "text/html; charset=utf-8")

    def http_get(self, url, payload=None, verify_cert=False):
        resp = requests.get(url
                            , proxies=self.proxy.using_proxy
                            , headers=self._headers
                            , cookies=self._cookies
                            , params=payload
                            , timeout=self.out_time
                            , verify=verify_cert)
        if self.encoding:
            resp.encoding = self.encoding
        return resp

    def http_post(self, url, post_data, verify_cert=False):
        resp = requests.post(url
                             , proxies=self.proxy.using_proxy
                             , headers=self._headers
                             , cookies=self._cookies
                             , data=post_data
                             , timeout=self.out_time
                             , verify=verify_cert)
        if self.encoding:
            resp.encoding = self.encoding
        return resp
