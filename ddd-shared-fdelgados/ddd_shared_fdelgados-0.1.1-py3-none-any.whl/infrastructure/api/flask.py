from typing import Optional, Dict
from flask import make_response, jsonify
from http import HTTPStatus


def error_response(code: int,
                   message: str,
                   status: Optional[int] = HTTPStatus.INTERNAL_SERVER_ERROR,
                   trace_id: Optional[str] = "",
                   headers: Optional[Dict] = None):

    if headers is None:
        headers = {}

    error = {"status": status,
             "code": code,
             "message": message}

    if trace_id:
        error["trace_id"] = trace_id

    response = make_response(jsonify(error=error), status)

    if status == HTTPStatus.UNAUTHORIZED:
        headers["WWW-Authenticate"] = "Bearer realm=\"API\", charset=\"UTF-8\""

    if not headers:
        return response

    for name, value in headers.items():
        response.headers[name] = value

    return response
