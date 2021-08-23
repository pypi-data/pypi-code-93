from typing import Optional
from enum import Enum
from tracardi.process_engine.tql.utils.dictonary import flatten
from pydantic import AnyHttpUrl, BaseModel


class Method(str, Enum):
    post = "post"
    get = "get"
    put = "put"
    delete = 'delete'


class RemoteCallConfiguration(BaseModel):
    url: AnyHttpUrl
    timeout: int = 30
    method: Method = Method.get
    headers: Optional[dict] = {}
    cookies: Optional[dict] = {}
    sslCheck: bool = True

    def get_params_as_json(self, params):
        if self.method == 'get':
            params = flatten(params)
            return {
                "params": params
            }

        return {
            "json": params
        }
