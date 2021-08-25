from typing import Callable
from flask import Response
from jsonclasses_flask.settings import CorsSetting


def add_cors_headers(cors: CorsSetting) -> Callable[[Response], Response]:
    def handler(response: Response) -> Response:
        res = response
        res.headers['Access-Control-Allow-Origin'] = cors.get('allow_origin') or '*'
        return res
    return handler
