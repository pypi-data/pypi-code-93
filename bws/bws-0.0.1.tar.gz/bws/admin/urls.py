from functools import wraps
from flask import jsonify, Response
from flask_admin import expose


def json_render(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        body = f(*args, **kwargs)
        try:
            if not isinstance(body, Response):
                return jsonify(body)
            return body
        except Exception as e:
            return body

    return decorated_view


def expose_json(url='/', methods=('GET',)):
    """
        Use este decorador para responder json
    """
    def wrap(f):
        if not hasattr(f, '_urls'):
            f._urls = []
        f._urls.append((url, methods))

        return json_render(f)
    return wrap


__all__ = [
    "expose",
    "json_render",
    "expose_json" ,  
]
