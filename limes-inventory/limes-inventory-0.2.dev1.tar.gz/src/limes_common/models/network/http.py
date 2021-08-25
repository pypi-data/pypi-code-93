from limes_common.models.network.endpoints import Endpoint
from . import Model


class HttpRequest(Model):
    def __init__(self, endpoint: Endpoint) -> None:
        super().__init__()
        self._endpoint = endpoint

class HttpTransaction:
    class Request(HttpRequest):
        pass

    class Response(Model):
        pass

    # this doesn't convey typing
    @classmethod
    def GetParser(cls):
        return cls.Response.Parse