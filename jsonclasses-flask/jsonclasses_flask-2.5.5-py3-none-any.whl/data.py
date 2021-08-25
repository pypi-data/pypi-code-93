from typing import Optional, Any
from flask import jsonify, Response


def data(arg: Optional[Any] = None) -> Response:
    return jsonify(data=arg)
