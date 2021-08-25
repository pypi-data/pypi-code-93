import requests as Requests
import uuid
from getpass import getuser
import os
from typing import Any, Callable, TypeVar, Union

from limes_common.connections import Criteria
from limes_common.models.basic import AbbreviatedEnum
from ..http import HttpConnection, SessionMethod
from ... import config
from ...models.network import Model, ErrorModel, Primitive, server as Models, provider
from ...models.network.endpoints import ServerEndpoint

T = TypeVar('T')
class ServerConnection(HttpConnection):
    def __init__(self) -> None:
        super().__init__(config.SERVER_URL, [
            Criteria.ALL
        ])

        self._id = ('%012x:%s:%s' % (uuid.getnode(), getuser(), os.getppid()))
        self._csrf = ''
        try:
            raw = self.session.get(self._makeUrl(ServerEndpoint.INIT))
            res = Models.Init.Response.Parse(raw)
            if res._responseCode == 200:
                self._csrf = res.CsrfToken
            self.Ready = True
        except Requests.exceptions.ConnectionError:
            print('*** limes server is not reachable ***')
            self.Ready = False

    def _makeHeader(self):
        return {config.CSRF_NAME: self._csrf}

    def _makeJson(self, data: Models.ServerRequest) -> dict[str, Any]:
        data.ClientId = self._id
        d = data.ToDict()
        # d[config.CSRF_NAME] = self._csrf
        return d

    def Send(self, reqModel: Models.ServerRequest, parser: Callable[..., T],
            req: SessionMethod=SessionMethod.POST) -> Union[T, ErrorModel]:
        return super().Send(reqModel, parser, req=req)

    def Authenticate(self):
        return self.Send(
            Models.Authenticate.Request(self._id),
            Models.Authenticate.Response.Parse
        )

    # def CheckStatus(self, msg: str='') -> provider.Status.Response:
    #     res = self.Authenticate()
    #     if not isinstance(res, ErrorModel):
    #         return provider.Status.Response(res.Success, msg='%s %s' % (res.FirstName, res.LastName))
    #     return provider.Status.Response(False)

    # def GetSchema(self) -> provider.Schema:
    #     raise AbstractClassException(_notImplimentedMsg)

    # def MakeRequest(self, purpose: str, request: Primitive) -> Primitive:
    #     raise AbstractClassException(_notImplimentedMsg)
