# -*- coding: utf-8 -*-

from fastapi.responses import UJSONResponse

from hagworm.extend.base import Utils
from hagworm.extend.struct import Result


class Response(UJSONResponse):

    def __init__(self, content=None, status_code=200, *args, **kwargs):

        self._request_id = Utils.uuid1_urn()

        super().__init__(content, status_code, *args, **kwargs)

    @property
    def request_id(self):

        return self._request_id

    def render(self, content):
        return super().render(
            Result(data=content, request_id=self._request_id)
        )


class ErrorResponse(Response, Exception):

    def __init__(self, error_code, content=None, status_code=200, **kwargs):

        self._error_code = error_code

        Response.__init__(self, content, status_code, **kwargs)
        Exception.__init__(self, self.body.decode())

    def render(self, content):
        return UJSONResponse.render(
            self,
            Result(code=self._error_code, data=content, request_id=self._request_id)
        )
