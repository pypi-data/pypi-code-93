import json
import types

import httpx


def serialize_object(self):
    return {
        attr: getattr(self, attr)
        for attr in dir(self)
        if not (attr.startswith('_') or isinstance(getattr(self, attr), types.MethodType))
    }


class Mapper:

    def json(self):
        return serialize_object(self)

    def __str__(self):
        return json.dumps(self.json())


class RequestMapper(Mapper):

    def __init__(self, response: httpx.Response):
        self.__http_response__ = response
        self.method = response.request.method
        self.url = str(response.url)

    @property
    def body(self):

        try:
            payload = self.__http_response__.request.stream._body
        except AttributeError:
            return
        try:
            return json.loads(payload)
        except json.decoder.JSONDecodeError:
            return payload

    @property
    def headers(self):
        return {k: v for k, v in self.__http_response__.request.headers.items()}


class ResponseMapper(Mapper):

    def __init__(self, response: httpx.Response):
        self.__http_response__ = response
        self.status = response.status_code

    def json(self):
        return serialize_object(self)

    def __str__(self):
        return json.dumps(self.json())

    @property
    def headers(self) -> dict:
        return {key: value for key, value in self.__http_response__.headers.items()}

    @property
    def body(self):
        try:
            return self.__http_response__.json()
        except json.decoder.JSONDecodeError:
            return self.__http_response__.text


class HTTPTrafficMapper(Mapper):

    def __init__(self, response: httpx.Response):
        self.__http_response__ = response
        self.response = ResponseMapper(response)
        self.request = RequestMapper(response)

    def json(self):
        return dict(request=self.request.json(), response=self.response.json())
