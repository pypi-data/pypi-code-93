from typing import List

from pydantic import BaseModel


class NameSpaces(BaseModel):
    Namespace: List[str]
