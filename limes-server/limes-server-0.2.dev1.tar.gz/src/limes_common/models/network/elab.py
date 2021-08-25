import json
from typing import TypeVar, Callable, Any
from requests import Response

from . import PublicModel, _tryParse



class Login:
    @classmethod
    def MakeRequest(cls, username: str, password: str):
        return {
            'username': username,
            'password': password,
        }

    class Response(PublicModel):
        def __init__(self, res: Response) -> None:
            super().__init__(res)
            self.Success = self.Code==200
            self.Token = _tryParse(str, self.data, 'token', '')
            userData = self.data['user'] if self.Success else {}
            self.FirstName = _tryParse(str, userData, 'firstName', '')
            self.LastName = _tryParse(str, userData, 'lastName', '')

class SampleModel:
    def __init__(self, data: dict = {}) -> None:
        self.Name = _tryParse(str, data, 'name', 'None')
        self.Owner =_tryParse(str, data, 'owner', '')
        self.TimeCreated =_tryParse(str, data, 'created', '')
        self.Id =_tryParse(int, data, 'sampleID', 0)
        self.Barcode =_tryParse(str, data, 'barcode', '')
        self.Description =_tryParse(str, data, 'description', '')
        self.ParentId =_tryParse(int, data, 'parent', 0)

class Sample:
    class ListResponse(PublicModel):
        def __init__(self, res: Response) -> None:
            super().__init__(res)
            # self.Samples = list(map(lambda raw: SampleModel(raw), self.data))
            self.Samples = list(map(lambda raw: SampleModel(raw), self.data.get('data', [])))

    class Response(PublicModel):
        def __init__(self, res: Response) -> None:
            super().__init__(res)
            self.Sample = SampleModel(self.data)


class MetaField:
    def __init__(self, data: dict = {}) -> None:
        T = TypeVar('T')
        def parse (constr, key):
            defaults = {
                bool: False,
                str: '',
                int: 0,
            }
            return _tryParse(constr, data, key, defaults[constr])
        self.raw = data
        self.archived: bool = parse(bool, 'archived')
        self.sampleMetaID: int = parse(int, 'sampleMetaID')
        self.sampleDataType: str = parse(str, 'sampleDataType') # todo, make enum
        self.key: str = parse(str, 'key')
        self.value: str = parse(str, 'value')
        self.sampleTypeMetaID: int = parse(int, 'sampleTypeMetaID')
        self.truncated: bool = parse(bool, 'truncated')

    def ToDict(self) -> dict:
        out = self.__dict__.copy()
        keys = list(out.keys())
        for k in keys:
            if k.startswith('_') or k in ['raw']:
                del out[k]
        return out

class SampleMeta:
    class Response(PublicModel):
        def __init__(self, res: Response) -> None:
            super().__init__(res)
            self.Fields: dict[str, MetaField] = {}
            for raw in self.data['data']:
                self.Fields[raw['key']] = MetaField(raw)

    class UpdateResponse(PublicModel):
        def __init__(self, res: Response) -> None:
            super().__init__(res)
            self.Success = self.Code == 204