import json

import logging

import requests
from requests.structures import CaseInsensitiveDict

from bbcloud_python_sdk.Api.Exceptions import ParameterErrorException, MethodNotAllowedErrorException


class Http():
    def __init__(self, client):
        self.client = client

    def set_request_path(self, request_path):
        self.request_path = request_path
        return self

    def get_request_url(self):
        return '%s/%s' % (self.client.base_url, self.request_path)

    def set_request_query(self, query):
        self.query = query
        return self

    def set_params(self, params):
        self.params = params
        return self

    def get(self):
        res = self.do_request(
            req=Request(
                method='GET',
                url=self.get_request_url(),
                client=self.client,
                params=self.query
            )
        )
        if res:
            return res.get('data', [])

    def do_request(self, req, timeout=10):
        res = requests.request(req.method, req.url,
                               data=req.data,
                               params=req.params,
                               headers=req.headers,
                               stream=True,
                               timeout=timeout)
        return Response(res).read()

    def create(self, data):
        res = self.do_request(
            req=Request(
                method='POST',
                url=self.get_request_url(),
                client=self.client,
                data=json.dumps(data)
            )
        )
        return res

    def patch(self, id, data):
        res = self.do_request(
            req=Request(
                method='PATCH',
                url='%s/%s' % (self.get_request_url(), id),
                client=self.client,
                data=json.dumps(data)
            )
        )
        return res

    def delete(self, id):
        res = self.do_request(
            req=Request(
                method='DELETE',
                url='%s/%s' % (self.get_request_url(), id),
                client=self.client
            )
        )
        return res == 1


class Request(object):
    def __init__(self, method, url, client,
                 data=None,
                 params=None,
                 headers=None):
        self.method = method
        self.url = url
        self.data = data
        self.params = params or {}

        if not isinstance(headers, CaseInsensitiveDict):
            self.headers = CaseInsensitiveDict(headers)
        else:
            self.headers = headers

        self.headers['Content-Type'] = 'application/json;charset=UTF-8'

        self.headers['Authorization'] = 'Bearer %s' % (client.token)

        if client._auth_team:
            self.headers['Auth-team'] = client._auth_team

        if client._auth_application:
            self.headers['Auth-team'] = client._auth_application

        if client._auth_namespace:
            self.headers['Auth-team'] = client._auth_namespace

        logging.debug(self.method)
        logging.debug(self.headers)
        logging.debug(self.params)


class Response(object):
    def __init__(self, response):

        self.response = response
        self.status = response.status_code
        self.headers = response.headers
        if self.status == 422:
            raise ParameterErrorException(self.read())
        if self.status == 405:
            raise MethodNotAllowedErrorException(
                '%s method not allowed for %s' % (response.request.method, response.url)
            )

    def read(self):
        return json.loads(self.response.content)
