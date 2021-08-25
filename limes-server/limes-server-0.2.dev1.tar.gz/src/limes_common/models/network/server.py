from __future__ import annotations

from limes_common.connections import Criteria
from limes_common.models.basic import AbbreviatedEnum
from limes_common.models.network import provider as Providers
from limes_common.models.network.endpoints import ServerEndpoint
from limes_common.models.network.http import HttpRequest, HttpTransaction
from . import Model, SerializableTypes, Primitive

class Init(HttpTransaction):
    class Response(Model):
        def __init__(self, token: str = '') -> None:
            super().__init__()
            self.CsrfToken = token

class ServerRequest(HttpRequest):
    def __init__(self, endpoint: ServerEndpoint) -> None:
        super().__init__(endpoint)
        self.ClientId = ''

class Authenticate(HttpTransaction):
    class Request(ServerRequest):
        def __init__(self, clientId: str = '') -> None:
            super().__init__(ServerEndpoint.AUTHENTICATE)
            self.ClientId = clientId

    class Response(Model):
        def __init__(self, success: bool=False, token: str='', firstName: str='', lastName: str='') -> None:
            super().__init__()
            self.Success = success
            self.Token = token
            self.FirstName = firstName
            self.LastName = lastName

class Login(HttpTransaction):
    class Request(ServerRequest):
        def __init__(self, eLabKey: str='', firstName: str='', lastName: str='') -> None:
            super().__init__(ServerEndpoint.LOGIN)
            self.ELabKey = eLabKey
            self.FirstName = firstName
            self.LastName = lastName

    class Response(Model):
        def __init__(self, success: bool=False) -> None:
            super().__init__()
            self.Success = success

    Parse = Response.Parse

class AddSample(HttpTransaction):
    class Request(ServerRequest):
        def __init__(self, file: str='', sampleId: str='', name: str='') -> None:
            super().__init__(ServerEndpoint.ADD)
            self.File = file
            self.SampleId = sampleId
            self.Name = name

    class Response(Model):
        def __init__(self, success: bool=False, sampleName: str='', message: str='') -> None:
            super().__init__()
            self.Success = success
            self.SampleName = sampleName
            self.Message = message

class ProviderInfo(Model):
    def __init__(self, name: str='', lastUse: float=0, schema: Providers.Schema=Providers.Schema()) -> None:
        self.Name = name
        self.LastUse = lastUse
        self.Schema = schema

class List(HttpTransaction):
    class Request(ServerRequest):
        def __init__(self) -> None:
            super().__init__(ServerEndpoint.LIST)

    class Response(Model):
        def __init__(self, providers: list[ProviderInfo]=[]) -> None:
            super().__init__()
            self.Providers = providers
            
        @classmethod
        def Parse(cls, serialized: bytes | str | dict, typesDict: type[SerializableTypes]=None):
            if typesDict is None: typesDict = ServerSerializableTypes 
            return super().Parse(serialized, typesDict=typesDict)

class Search(HttpTransaction):
    class Request(ServerRequest):
        def __init__(self, query: str | list[str] = '', criteria: list[Criteria]=[]) -> None:
            super().__init__(ServerEndpoint.SEARCH)
            self.Query = query
            self.Criteria = criteria

    class Hit(Model):
        def __init__(self, type: str='', data: dict[str, Primitive]={}) -> None:
            self.Type = type
            self.Data = data

    class Response(Model):
        def __init__(self, hits: list[Search.Hit]=[]) -> None:
            super().__init__()
            self.Hits = hits

        @classmethod
        def Parse(cls, serialized, typesDict: type[SerializableTypes]=None):
            if typesDict is None: typesDict = ServerSerializableTypes
            return super().Parse(serialized, typesDict=typesDict)

class CallProvider(HttpTransaction):
    class Request(ServerRequest):
        def __init__(self, providerName: str='', body: Providers.Generic=Providers.Generic()) -> None:
            super().__init__(ServerEndpoint.CALL)
            self.Body = body
            self.Provider = providerName

    # response is just a Providers.Generic

class ServerSerializableTypes(Providers.ProviderSerializableTypes):
    PROVIDER_INFO = ProviderInfo.Parse, ProviderInfo()
    SEARCH_HIT = Search.Hit.Parse, Search.Hit()
