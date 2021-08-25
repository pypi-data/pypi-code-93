from typing import Any
from flask import Response, make_response


def empty(*args: Any, **kwargs: Any) -> Response:
    return make_response('', 204)
