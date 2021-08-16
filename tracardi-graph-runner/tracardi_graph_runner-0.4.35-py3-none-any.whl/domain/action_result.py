from typing import Any
from pydantic import BaseModel


class ActionResult(BaseModel):
    port: str
    value: Any

    class Config:
        allow_mutation = False
