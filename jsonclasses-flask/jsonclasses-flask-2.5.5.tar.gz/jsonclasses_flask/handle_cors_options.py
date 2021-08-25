from typing import Callable, Optional
from flask import request, Response, current_app
from .settings import CorsSetting


def handle_cors_options(cors: CorsSetting) -> Callable[[], Optional[Response]]:
    def handler():
        if request.method == 'OPTIONS':
            res = current_app.response_class()
            res.status_code = 204
            res.headers['Access-Control-Allow-Origin'] = cors.get('allow_origin') or '*'
            res.headers['Access-Control-Allow-Methods'] = cors.get('allow_methods') or 'OPTIONS, POST, GET, PATCH, DELETE'
            res.headers['Access-Control-Allow-Headers'] = cors.get('allow_headers') or '*'
            res.headers['Access-Control-Max-Age'] = '86400'
            return res
    return handler
