from flask import g
from werkzeug.exceptions import Unauthorized


async def ensure_operator():
    if g.operator is None:
        raise Unauthorized('sign in required')
