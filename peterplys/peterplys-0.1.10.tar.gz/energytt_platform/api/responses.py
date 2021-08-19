from functools import partial


class HttpResponse(object):
    def __init__(self, status: int, msg: str = ''):
        self.status = status
        self.msg = msg

    @classmethod
    def build(cls, *args, **kwargs):
        return partial(cls, *args, **kwargs)


class HttpError(HttpResponse, Exception):
    def __init__(self, msg: str, status_code: int):
        super(HttpError, self).__init__('%d %s' % (status_code, msg))
        self.msg = msg
        self.status_code = status_code

    @classmethod
    def build(cls, status_code: int):
        return partial(cls, status_code=status_code)


BadRequest = HttpError.build(400)
Unauthorized = HttpError.build(401)
InternalServerError = HttpError.build(500)
