from __future__ import annotations
from typing import Union

from . import Model, SerializableTypes, Primitive

class Message(Model):
    def __init__(self, mid: str='', body: str='', isError:bool=False) -> None:
        self.MessageID = mid
        self.Body = body
        self.IsError = isError

class Status:
    class Request(Model):
        def __init__(self, msg: str = '') -> None:
            super().__init__()
            self.Msg = msg

    class Response(Model):
        def __init__(self, online: bool=False, echo: str='', msg: str='') -> None:
            super().__init__()
            self.Online = online
            self.Echo = echo
            self.Msg = msg

# class Fields:
#     def __init__(self, fields: list[tuple[str, type]] = []) -> None:
#         self._fields = {}
#         for n, t in fields:
#             self._fields[n] = t

#     def AsDict(self) -> dict[str, type]:
#         return self._fields

DataSchema = Union[type, dict[str, 'DataSchema']]
class Service(Model):
    def __init__(self, name: str='', input: DataSchema={}, output: DataSchema={}) -> None:
        self.Name = name
        def cleanTypes(d: DataSchema) -> Primitive:
            if isinstance(d, dict):
                out = {}
                for k in d.keys():
                    v = d[k]
                    v = cleanTypes(v)
                    out[k] = v
            else:
                raw = str(d)
                if '<class' in raw:
                    out = raw[8:-2] # "<class 'type'>" to just "type"
                else:
                    out = raw
            return out

        self.Input = cleanTypes(input)
        self.Output = cleanTypes(output)

class Schema(Model):
    def __init__(self, services: list[Service]=[]) -> None:
        self.Services = services
    
    @classmethod
    def Parse(cls, serialized, typesDict: type[SerializableTypes]=None):
        if typesDict is None:
            typesDict = ProviderSerializableTypes
        return super().Parse(serialized, typesDict)
        
class Generic(Model):
    def __init__(self, purpose: str='None', data: Primitive={}) -> None:
        super().__init__()
        self.Purpose = purpose
        self.Data = data
    
    @classmethod
    def Parse(cls, serialized, typesDict: type[SerializableTypes]=None):
        if typesDict is None:
            typesDict = ProviderSerializableTypes
        return super().Parse(serialized, typesDict=typesDict)

class ProviderSerializableTypes(SerializableTypes):
    SCHEMA = Schema.Load, Schema()
    SERVICE = Service.Parse, Service()