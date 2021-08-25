import requests as Requests
from typing import Callable, TypeVar, Union

from limes_common.models.basic import AbbreviatedEnum
from limes_common.connections import Connection, Criteria
from limes_common.models.network import ErrorModel, Model
from limes_common.models.network.endpoints import Endpoint
from limes_common.models.network.http import HttpRequest

class SessionMethod(AbbreviatedEnum):
    GET = 1
    POST = 2

T = TypeVar('T')
class HttpConnection(Connection):
    def __init__(self, url, searchableCriteria: list[Criteria]) -> None:
        super().__init__(searchableCriteria)
        self.session = Requests.session()
        self._URL: str = url

    def _makeUrl(self, ep: Endpoint):
        return (self._URL if self._URL.endswith('/') else self._URL[:-1]) + ep.Path

    def _makeJson(self, data: Model) -> dict:
        d = data.ToDict()
        # d[config.CSRF_NAME] = self._csrf
        return d

    def _makeHeader(self):
        return {}

    def Send(self, reqModel: HttpRequest, constr: Callable[..., T], req: SessionMethod=SessionMethod.POST) -> Union[T, ErrorModel]:
        url = reqModel._endpoint 
        switcher = {
            SessionMethod.GET: self.session.get,
            SessionMethod.POST: self.session.post
        }
        return constr(switcher[req](
            self._makeUrl(url),
            json=self._makeJson(reqModel),
            headers = self._makeHeader()
        ))