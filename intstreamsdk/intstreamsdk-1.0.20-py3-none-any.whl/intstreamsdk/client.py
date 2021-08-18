import requests
from datetime import datetime
from requests_futures.sessions import FuturesSession
import base64
import json
import os


class RequestError(Exception):
    def __init__(self,message):
        super(Exception,self).__init__(message)
        self.message = message


class IntstreamException(Exception):
    pass


class ExclusiveParameters(IntstreamException):
    pass


class Client(object):
    REFRESH = 240 # 4 minutes less than time out for async request compatibility
    GET = "GET"
    POST = "POST"
    AUTH_JWT = "JWT"
    AUTH_OAUTH = "OAUTH"
    FORMAT_JSON = "application/json"
    FORMAT_XML = "application/xml"
    FORMAT_MULTIPART= "multipart/form-data"

    def __init__(self, server_url: str,
                 username: str=None,
                 password: str=None,
                 access: str=None,
                 refresh: str=None,
                 format: str=FORMAT_JSON,
                 timeout=60
                 ):
        """
        username and password OR access and refresh
        :param server_url:
        :param username:
        :param password:
        :param access:
        :param refresh:
        :param format:
        """
        if (username is not None or password is not None) \
                and (access is not None or refresh is not None):
            raise ExclusiveParameters

        self.username = username
        self.password = password
        self.login_data = {"username": self.username,"password": self.password}
        self.server_url = server_url + "/" if server_url[-1] != "/" else server_url
        self.session = None  # request session  or future session
        self.timeout=timeout

        self.header_format=format

        self.access_token = access
        self.refresh_token = refresh

        self.access_header= None
        self.access_payload= None
        self.access_sig= None

        self.refresh_header=None
        self.refresh_payload=None
        self.refresh_sig=None

        self.expire = None
        if self.refresh_token is not None:
            self.expire = self.get_expire(self.refresh_token)

        #todo use dict to map initialize, refresh_call, set_keys
        # this way can switch between oauth and jwt

    def get_expire(self, refresh_token):
        refresh_parts = refresh_token.split(".")
        refresh_payload=base64.urlsafe_b64decode(refresh_parts[1].encode('ascii')+b'===')
        expire = json.loads(refresh_payload)['exp']
        return expire

    def get_tokens(self):
        headers={}
        headers["Content-Type"]=self.header_format
        pre_r = self.session.post(self.server_url+"api/token-auth/",
                              json=self.login_data, headers=headers)
        r = self.get_actual_response(pre_r)
        if r.status_code == requests.codes.ok:
            self._set_keys(r)
        else:
            raise RequestError("initialize failed:" + str(r.status_code) + " " + r.text)

    def refresh_call(self):
        """
        jwt refresh call
        :return:
        """
        headers={}
        headers["Content-Type"]=self.header_format
        data = {"refresh":self.refresh_token}
        r = self.session.post(self.server_url+"api/token-refresh/",
                                 json=data,
                                 headers=headers, timeout=120)
        if r.status_code == requests.codes.ok:
            self._set_keys(r)
        else:
            raise RequestError("refresh failed:" + str(r.status_code) + " " + r.text)

    @staticmethod
    def get_actual_response(response):
        """
        will return actual data from request
        :return:
        """
        raise NotImplemented("not implemented")

    def initialize(self):
        """
        if not self.access then call _set_keys after making request for authorization
        :return:
        """
        if not self.access_token:
            self.get_tokens()

    def _set_keys(self, response:requests.Response):
        """
        jwt set keys
        :param response:
        :return:
        """
        if response.status_code == requests.codes.ok:
            self.access_token = response.json()["access"]
            access_parts = self.access_token.split(".")
            self.access_header= base64.urlsafe_b64decode(access_parts[0].encode('ascii')+b'===')
            self.access_payload= base64.urlsafe_b64decode(access_parts[1].encode('ascii')+b'===')
            self.access_sig= base64.urlsafe_b64decode(access_parts[2].encode('ascii')+b'===')

            if "refresh" in response.json():
                self.refresh_token = response.json()["refresh"]
                refresh_parts = self.refresh_token.split(".")
                self.refresh_header=base64.urlsafe_b64decode(refresh_parts[0].encode('ascii')+b'===')
                self.refresh_payload=base64.urlsafe_b64decode(refresh_parts[1].encode('ascii')+b'===')
                self.refresh_sig=base64.urlsafe_b64decode(refresh_parts[2].encode('ascii')+b'===')
                self.expire = self.get_expire(self.refresh_token)
        else:
            raise RequestError("set keys failed: " + str(response.status_code) + " " + str(response.text))

    def request(self, method, headers, request_url, params, json=None, files=None):
        """
        returns response and data for sync requests
        json and data are mutually exclusive
        :param rasise_exc: bool
        :return:
        """
        expired = True
        if self.expire is None:
            expired = True
        else:
            expired = True if datetime.utcnow().timestamp() > self.expire - 30 else False # 30 second buffer

        if expired:
            self.refresh_call()
        headers_req = {} if headers is None else headers
        headers_req["Authorization"]="Bearer "+self.access_token
        if files is None:
            headers_req["Content-Type"]=self.header_format
        r = self.session.request(method=method,
                                     headers=headers_req,
                                     url=request_url,
                                     params=params,
                                     json=json,
                                     files=files,
                                 timeout=self.timeout)
        return r



class AsyncClient(Client):
    def __init__(self,
                 server_url:str,
                 username:str,
                 password:str,
                 access=None,
                 refresh=None,
                 proxies:str=None,
                 verify:bool=True,
                 timeout=120,
                 format: str=Client.FORMAT_JSON,
                ):
        """
        :param server_url:
        :param username:
        :param password:
        :param proxies: dict of proxy url for each protocol {"http":http://myproxy.com,"https":http://myproxy.com"}
        :param verify:
        """
        super(AsyncClient,self).__init__(server_url=server_url,
                                         username=username,
                                         access=access,
                                         refresh=refresh,
                                         password=password,
                                         format=format,
                                         timeout=timeout)
        self.session = FuturesSession()
        if proxies is not None:
            self.session.proxies=proxies
        if not verify:
            self.session.verify=verify
        self.initialize()


    @staticmethod
    def get_actual_response(response):
        """
        returns the actual response from the future
        :param self:
        :param response:
        :return:
        """
        return response.result()


class SyncClient(Client):

    def __init__(self,
                 server_url:str,
                 username:str,
                 password:str,
                 access=None,
                 refresh=None,
                 proxies:dict=None,
                 verify:bool=True,
                 format:str=Client.FORMAT_JSON,
                 timeout=120):
        """
        :param server_url:
        :param username:
        :param password:
        :param proxies: dict of proxy url for each protocol {"http":http://myproxy.com,"https":http://myproxy.com"}
        :param verify:
        """
        super(SyncClient,self).__init__(server_url=server_url,
                                        username=username,
                                        access=access,
                                        refresh=refresh,
                                        password=password,
                                        timeout=timeout,
                                        format=format)
        self.session = requests.session()
        if proxies is not None:
            self.session.proxies = proxies
        if not verify:
            self.session.verify = verify

        self.initialize()


    @staticmethod
    def get_actual_response(response):
        """
        returns the response
        :param response:
        :return:
        """
        return response


