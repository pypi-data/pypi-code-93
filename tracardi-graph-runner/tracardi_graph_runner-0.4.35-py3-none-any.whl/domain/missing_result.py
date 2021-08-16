from typing import Any
from pydantic import BaseModel


class MissingResult(BaseModel):
    port: str
    value: Any = None

    class Config:
        allow_mutation = False
