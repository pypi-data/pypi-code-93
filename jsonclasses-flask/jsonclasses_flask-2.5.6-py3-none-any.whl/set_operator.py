from flask import request, g, current_app
from werkzeug.exceptions import Unauthorized
from jwt import DecodeError
from jsonclasses.exceptions import ObjectNotFoundException
from .decode_jwt_token import decode_jwt_token


async def set_operator():
    if 'authorization' not in request.headers:
        g.operator = None
        return
    authorization = request.headers['authorization']
    token = authorization[7:]
    try:
        decoded = decode_jwt_token(token)
    except DecodeError:
        raise Unauthorized('Authorization token is invalid.')
    except ObjectNotFoundException:
        raise Unauthorized('User is not authorized.')
    g.operator = decoded
