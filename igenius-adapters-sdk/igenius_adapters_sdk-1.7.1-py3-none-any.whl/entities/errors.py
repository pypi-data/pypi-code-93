from typing import List, Mapping, Union

from pydantic import BaseModel


class ErrorObject(BaseModel):
    type: str
    message: Union[str, List, Mapping]


class ErrorPayload(BaseModel):
    error: ErrorObject
