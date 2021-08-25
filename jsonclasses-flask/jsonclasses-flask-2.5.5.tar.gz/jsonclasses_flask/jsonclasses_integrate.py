from __future__ import annotations
from typing import Optional
from flask import Flask
from .jsjson_encoder import JSJSONEncoder
from .exception_handler import exception_handler
from .handle_cors_options import handle_cors_options
from .add_cors_headers import add_cors_headers
from .set_operator import set_operator
from .settings import CorsSetting, OperatorSetting


def jsonclasses_integrate(app: Flask,
                          cors: Optional[CorsSetting] = None,
                          operator: Optional[OperatorSetting] = None) -> Flask:
    app.json_encoder = JSJSONEncoder
    app.register_error_handler(Exception, exception_handler)
    if cors is not None:
        app.before_request(handle_cors_options(cors))
        app.after_request(add_cors_headers(cors))
    if operator is not None:
        app.config['jsonclasses_operator_cls'] = operator['operator_cls']
        app.config['jsonclasses_encode_key'] = operator['encode_key']
        app.before_request(set_operator)
    return app
