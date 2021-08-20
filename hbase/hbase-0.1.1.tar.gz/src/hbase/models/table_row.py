from typing import List

from pydantic import BaseModel, Field

from ..utils import from_base64


class _CellItem(BaseModel):
    column: str
    timestamp: int
    value: str = Field(..., alias="$")


class _RowItem(BaseModel):
    key: str
    Cell: List[_CellItem]


class CellItem(BaseModel):
    column: str
    timestamp: int
    value: str


class RowItem(BaseModel):
    key: str
    Cell: List[CellItem]


class TableRow(BaseModel):
    Row: List[RowItem]


class _TableRow(BaseModel):
    Row: List[_RowItem]

    def from_base64(self):
        return TableRow(
            Row=[
                RowItem(
                    key=from_base64(ri.key),
                    Cell=[
                        CellItem(column=from_base64(ci.column), timestamp=ci.timestamp, value=from_base64(ci.value))
                        for ci in ri.Cell
                    ],
                )
                for ri in self.Row
            ]
        )
