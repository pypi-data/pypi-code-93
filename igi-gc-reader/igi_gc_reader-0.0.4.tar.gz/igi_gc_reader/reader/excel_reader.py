"""
Can't use a single lib as we need to support .xls (supported by xlrd) and 
.xlsx (supported by openpyxl). Will use as thin a wrapper as possible round 
these libraries.
"""
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, List, Union
import os

import xlrd
from xlrd.book import Book
from xlrd.sheet import Sheet
import openpyxl
from openpyxl.workbook.workbook import Workbook
from openpyxl.xml.constants import WORKSHEET_TYPE

from igi_gc_reader.reader.excel_address import ExcelAddress


@dataclass  # type: ignore
class IExcelReader(ABC):
    filepath: str
    sheet_name: str
    _wb: Union[Workbook, Book]
    _sheet: Union[WORKSHEET_TYPE, Sheet]

    @abstractmethod
    def read_cell(self, addr: ExcelAddress) -> Any:
        pass

    def set_sheet(self, name: str) -> Any:
        sheet_names = self.get_sheet_names()
        try:
            self._sheet = self.get_sheet_by_name(name)
            self.sheet_name = name
        except:
            raise ValueError(f"No sheet named '{name}' in current workbook (sheets: {sheet_names})")

    def has_value(self, addr: ExcelAddress) -> bool:
        """Returns true if cell is not empty or whitespace only."""
        val = self.read_cell(addr)
        return has_value(val)

    @abstractmethod
    def get_sheet_names(self) -> List[str]:
        pass

    @abstractmethod
    def get_sheet_by_index(self, idx: int) -> Union[WORKSHEET_TYPE, Sheet]:
        pass

    @abstractmethod
    def get_sheet_by_name(self, name: str) -> Union[WORKSHEET_TYPE, Sheet]:
        pass

    @abstractmethod
    def close(self):
        pass


def has_value(val: Any) -> bool:
    return val and not str(val).isspace()
    


@dataclass
class ExcelOldFormatReader(IExcelReader):
    filepath: str
    sheet_name: str = field(default="")
    _wb: Book = field(init=False)
    _sheet: Sheet = field(init=False)

    def __post_init__(self):
        self._wb = xlrd.open_workbook(self.filepath)
        if self.sheet_name:
            self._sheet = self.get_sheet_by_name(self.sheet_name)
        else:
            self._sheet = self.get_sheet_by_index(0)

    def get_sheet_names(self) -> List[str]:
        return self._wb.sheet_names() 

    def read_cell(self, addr: ExcelAddress) -> Any:
        try:
            return self._sheet.cell_value(rowx=addr.row_idx, colx=addr.col_idx)
        except IndexError:
            return None

    def get_sheet_by_index(self, idx: int) -> Sheet:
        return self._wb.sheet_by_index(idx)

    def get_sheet_by_name(self, name: str) -> Sheet:
        return self._wb.sheet_by_name(name)

    def close(self):
        self._wb.release_resources()
        del self._sheet
        del self._wb


@dataclass
class ExcelNewFormatReader(IExcelReader):
    filepath: str
    sheet_name: str = field(default="")
    _wb: Workbook = field(init=False)
    _sheet: WORKSHEET_TYPE = field(init=False)

    def __post_init__(self):
        self._wb = openpyxl.load_workbook(self.filepath)
        if self.sheet_name:
            self._sheet = self.get_sheet_by_name(self.sheet_name)
        else:
            self._sheet = self.get_sheet_by_index(0)

    def get_sheet_names(self) -> List[str]:
        return self._wb.sheetnames

    def read_cell(self, addr: ExcelAddress) -> Any:
        return self._sheet[addr.addr].value

    def get_sheet_by_index(self, idx: int) -> WORKSHEET_TYPE:
        return self._wb.worksheets[idx]

    def get_sheet_by_name(self, name: str) -> WORKSHEET_TYPE:
        return self._wb[name]

    def close(self):
        self._wb.close()
        del self._sheet
        del self._wb


def get_excel_reader(filepath: str, sheet: str = "") -> IExcelReader:
    ext = os.path.splitext(filepath)[-1].lower()
    if ext == '.xls':
        return ExcelOldFormatReader(filepath, sheet)
    elif ext in ['.xlsx', '.xlsm']:
        return ExcelNewFormatReader(filepath, sheet)
    raise NotImplementedError(f"No Excel reader setup to handle {ext} extension files for file: {filepath}.")
