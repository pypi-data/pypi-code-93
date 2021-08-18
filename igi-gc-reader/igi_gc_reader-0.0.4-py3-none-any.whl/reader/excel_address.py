""" 
Allow easy conversion between row/col indices and Excel style addresses.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import namedtuple
from typing import Dict, Tuple, ClassVar


Indices: Tuple[int,int] = namedtuple('Indices', ['row', 'col'])
col_to_index_cache: Dict[str, int] = {}
index_to_col_cache: Dict[int, str] = {}


@dataclass
class ExcelAddress():
    addr: str
    indices: Indices = field(init=False)
    ASCII_A: ClassVar[int] = 65

    def __post_init__(self):
        self.indices = self.to_indices(self.addr)

    def __str__(self) -> str:
        return self.addr

    @property
    def row_idx(self):
        return self.indices.row

    @property
    def col_idx(self):
        return self.indices.col
    
    @staticmethod
    def from_indices(indices: Indices) -> ExcelAddress:
        col = col_index_to_letter(indices.col)
        return ExcelAddress(f"{col}{str(indices.row+1)}")

    @staticmethod
    def to_indices(addr: str):
        if not addr:
            return Indices(-1, -1)
        col_letters, row_num_str = "", ""
        for char in addr.upper():
            if char.isalpha():
                col_letters += char
            elif char.isdigit(): 
                row_num_str += char
            else:
                raise ValueError(f"Failed to identify char ({char}) in cell address ({addr}) "
                                 f"as either letter or number.")

        col_idx = col_letter_to_index(col_letters)
        return Indices(row=int(row_num_str)-1, col=col_idx)


def col_index_to_letter(idx: int) -> str:
    global col_to_index_cache, index_to_col_cache
    if idx in index_to_col_cache:
        return index_to_col_cache[idx]

    mod = idx % 26  # handle e.g. col letter above Z
    prefix = ""
    if idx >= 26:
        n = int(idx / 26) - 1
        prefix = chr(n + ExcelAddress.ASCII_A)

        if n >= 26:
            raise NotImplementedError("Three letter columns not yet handled")
    
    col = prefix + chr(mod + ExcelAddress.ASCII_A)

    index_to_col_cache[idx] = col
    col_to_index_cache[col] = idx
    return col


def col_letter_to_index(col: str) -> int:
    global col_to_index_cache, index_to_col_cache
    if col in col_to_index_cache:
        return col_to_index_cache[col]

    letter_indices = [ord(l)-ExcelAddress.ASCII_A for l in col]
    idx = sum([idx if pos == 0 else (idx+1) * pow(26, pos) 
                    for pos, idx in enumerate(reversed(letter_indices))])

    index_to_col_cache[idx] = col
    col_to_index_cache[col] = idx    
    return idx


def next_col(col: str) -> str:
    """i.e. D -> C, Z -> AA etc"""
    return col_index_to_letter(col_letter_to_index(col) + 1)
