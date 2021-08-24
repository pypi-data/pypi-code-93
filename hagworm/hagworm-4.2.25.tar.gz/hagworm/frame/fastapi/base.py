# -*- coding: utf-8 -*-

import os
import fastapi

from starlette.types import Receive, Scope
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.exceptions import HTTPException

from fastapi import __version__ as fastapi_version
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from hagworm import hagworm_label, hagworm_slogan
from hagworm import __version__ as hagworm_version
from hagworm.extend.asyncio.base import Utils
from hagworm.extend.logging import DEFAULT_LOG_FILE_ROTATOR, init_logger

from .response import Response, ErrorResponse


DEFAULT_HEADERS = [(r'Server', hagworm_label)]


def create_fastapi(
        log_level=r'info', log_handler=None, log_file_path=None,
        log_file_rotation=DEFAULT_LOG_FILE_ROTATOR, log_file_retention=0xff,
        debug=False,
        routes=None,
        **setting
):

    init_logger(
        log_level.upper(),
        log_handler,
        log_file_path,
        log_file_rotation,
        log_file_retention,
        debug
    )

    environment = Utils.environment()

    Utils.log.info(
        f'{hagworm_slogan}'
        f'hagworm {hagworm_version}\n'
        f'fastapi {fastapi_version}\n'
        f'python {environment["python"]}\n'
        f'system {" ".join(environment["system"])}'
    )

    setting.setdefault(r'title', r'Hagworm')
    setting.setdefault(r'version', hagworm_version)

    _fastapi = fastapi.FastAPI(debug=debug, routes=routes, **setting)

    _fastapi.add_exception_handler(HTTPException, http_exception_handler)
    _fastapi.add_exception_handler(RequestValidationError, request_validation_exception_handler)

    return _fastapi


class APIRoute(fastapi.routing.APIRoute):

    def get_route_handler(self):

        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: fastapi.Request):

            try:
                return await original_route_handler(
                    Request(request.scope, request.receive, self)
                )
            except ErrorResponse as err:
                Utils.log.warning(f'ErrorResponse: {request.url.path}\n{err}')
                return err

        return custom_route_handler


class APIRouter(fastapi.APIRouter):
    """目录可选末尾的斜杠访问
    """

    def __init__(
            self,
            *,
            prefix=r'',
            default_response_class=Response,
            route_class=APIRoute,
            **kwargs
    ):

        super().__init__(
            prefix=prefix,
            default_response_class=default_response_class,
            route_class=route_class,
            **kwargs
        )

    def _get_path_alias(self, path):

        _path = path.rstrip(r'/')

        if not self.prefix and not _path:
            return [path]

        _path_split = os.path.splitext(_path)

        if _path_split[1]:
            return [_path]

        return [_path, _path + r'/']

    def api_route(self, path, *args, **kwargs):

        def _decorator(func):

            for index, _path in enumerate(self._get_path_alias(path)):

                self.add_api_route(_path, func, *args, **kwargs)

                # 兼容的URL将不会出现在docs中
                if index == 0:
                    kwargs[r'include_in_schema'] = False

            return func

        return _decorator


class Request(fastapi.Request):

    def __init__(self, scope: Scope, receive: Receive, api_route: APIRoute):

        super().__init__(scope, receive)

        self._api_route = api_route

    @property
    def route(self):

        return self._api_route

    @property
    def path(self):

        return self._api_route.path

    @property
    def tags(self):

        return self._api_route.tags

    @property
    def referer(self):

        return self.headers.get(r'Referer')

    @property
    def client_ip(self):

        if self.x_forwarded_for:
            return self.x_forwarded_for[0]
        else:
            return self.client_host

    @property
    def client_host(self):

        return self.headers.get(r'X-Real-IP', self.client.host)

    @property
    def x_forwarded_for(self):

        return Utils.split_str(self.headers.get(r'X-Forwarded-For', r''), r',')

    @property
    def content_type(self):

        return self.headers.get(r'Content-Type')

    @property
    def content_length(self):

        result = self.headers.get(r'Content-Length', r'')

        return int(result) if result.isdigit() else 0

    def get_header(self, name, default=None):

        return self.headers.get(name, default)


async def http_exception_handler(
        request: Request, exc: HTTPException
) -> ErrorResponse:

    headers = getattr(exc, r'headers', None)

    if headers:
        return ErrorResponse(
            -1,
            content={r'detail': exc.detail},
            status_code=exc.status_code,
            headers=headers
        )
    else:
        return ErrorResponse(
            -1,
            content={r'detail': exc.detail},
            status_code=exc.status_code
        )


async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
) -> ErrorResponse:

    return ErrorResponse(
        -1,
        content={r'detail': jsonable_encoder(exc.errors())},
        status_code=HTTP_400_BAD_REQUEST,
    )
