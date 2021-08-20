from typing import List

from pydantic import BaseModel


class TableItem(BaseModel):
    name: str


class Tables(BaseModel):
    table: List[TableItem]
