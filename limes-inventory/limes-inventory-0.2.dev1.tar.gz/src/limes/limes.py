from typing import Any, Union
import os

from limes.tools.qol import Switch
from limes_common.connections import Criteria

from limes_common.connections.statics import ELabConnection, ServerConnection
from limes_common.models.network import Primitive, server, ErrorModel, Model
from limes_common.models.network.elab import SampleModel

class Limes:
    def __init__(self) -> None:
        self._server = ServerConnection()
        self._eLab = ELabConnection()

    #   def _auth() -> tuple[bool, str]:
    def _auth(self) -> bool:
        res = self._server.Authenticate()
        if isinstance(res, ErrorModel):
            return False
        if res.Success:
            print('Authenticated terminal as %s' % res.FirstName)
            # return True, res.FirstName
            self._eLab.SetToken(res.Token)
        else:
            # return False, ''
            print('Not logged in')
        return res.Success
                

    def Login(self, username, password) -> bool:
        if not self._server.Ready: return False
        res = self._eLab.Login(username, password)

        if res.Success:
            self._server.Send(
                server.Login.Request(res.Token, res.FirstName, res.LastName),
                server.Login.Parse
            )
            print('logged in terminal as %s' % res.FirstName)
        return res.Success

    def ListProviders(self):
        if not self._server.Ready: return None
        return self._server.Send(
            server.List.Request(),
            server.List.Response.Parse
        )

    def Search(self, token: str, criteria: list[Criteria]=[]):
        # res = self._eLab.SearchSamples(token)
        res = self._server.Send(
            server.Search.Request(token, criteria),
            server.Search.Response.Parse
        )
        # search locations
        # search providers
        return res

    def AddSample(self):
        pass

    def DeleteSample(self):
        pass

    def CallProvider(self):
        pass

    # def Add(self, sampleId: str, path: str, fileName: str=None) -> bool:
    #     if not self._server.Ready: return False

    #     if fileName is None:
    #         tokens = path.split('/')
    #         fileName = tokens[len(tokens) - 1]

    #     path = os.path.abspath(path)
    #     file = open(path, 'rb')
    #     res = self._server.Add(sampleId, path, fileName, file)

    #     if not res.Success:
    #         print(res.Message)
    #     else:
    #         print('file [%s] added to sample [%s]' % (fileName, res.SampleName))
    #     return res.Success

    def dLogin(self) -> None:
        with open('../../credentials/elab.msl') as cred:
            lines = cred.readlines()
            lines = list(map(lambda l: l.replace('\n', ''), lines))
            if not self.Login(lines[0], lines[1]):
                print('quick login failed')