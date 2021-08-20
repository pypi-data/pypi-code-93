import dataclasses
import json
from abc import ABC, abstractmethod
from typing import Optional, Union

import pydantic

from jsonrpcstdio.errors import catch_and_throw, ParseError, InvalidRequestError
from pydantic.dataclasses import dataclass


class Message(ABC):
    @property
    def jsonrpc(self):
        return '2.0'

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes):
        pass

    @abstractmethod
    def encode(self) -> bytes:
        pass


@dataclass
class Request(Message):
    id: Union[int, str]
    method: str
    params: Union[list, dict, None] = None

    @classmethod
    @catch_and_throw(pydantic.ValidationError, InvalidRequestError)
    @catch_and_throw(json.JSONDecodeError, ParseError)
    def decode(cls, data: bytes):
        data = json.loads(data)
        return cls(
            id=data['id'], method=data['method'], params=data.get('params')
        )

    def encode(self) -> bytes:
        data = {'jsonrpcstdio': self.jsonrpc, 'id': self.id, 'method': self.method}
        if self.params is not None:
            data['params'] = self.params
        return json.dumps(data).encode()


@dataclass
class Notification(Message):
    method: str
    params: Union[list, dict, None] = None

    @classmethod
    @catch_and_throw(pydantic.ValidationError, InvalidRequestError)
    @catch_and_throw(json.JSONDecodeError, ParseError)
    def decode(cls, data: bytes):
        data = json.loads(data)
        return cls(
            method=data['method'], params=data.get('params')
        )

    def encode(self) -> bytes:
        data = {'jsonrpcstdio': self.jsonrpc, 'method': self.method}
        if self.params is not None:
            data['params'] = self.params
        return json.dumps(data).encode()


@dataclass
class ResponseError:
    code: int
    message: str
    data: Union[str, int, float, dict, list, None] = None

    @classmethod
    def from_data(cls, data: dict):
        return cls(code=data['code'], message=data['message'], data=data.get('data'))

    def todict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class Response(Message):
    id: Union[int, str, None]
    result: Union[str, int, float, dict, None] = None
    error: Optional[ResponseError] = None

    @classmethod
    def decode(cls, data: bytes):
        data = json.loads(data)
        res, err = data.get('result'), data.get('error')
        if res and err:
            ValueError('Response must contain either a result or an error, not both.')
        return cls(id=data.get('id'), result=res, error=ResponseError.from_data(err))

    def encode(self) -> bytes:
        data = {'jsonrpcstdio': self.jsonrpc, 'id': self.id}
        if self.result is not None:
            data['result'] = self.result
        if self.error is not None:
            data['error'] = {'code': self.error.code,
                             'message': self.error.message}
            if self.error.data:
                data['error']['data'] = self.error.data
        return json.dumps(data).encode()
