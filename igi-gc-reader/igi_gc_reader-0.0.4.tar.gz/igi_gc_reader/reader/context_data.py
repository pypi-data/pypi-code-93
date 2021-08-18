from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from types import coroutine
from typing import ClassVar, Dict, List, Optional, Tuple, Any

from igi_gc_reader.reader.excel_reader import IExcelReader, has_value
from igi_gc_reader.reader.excel_address import ExcelAddress
from igi_gc_reader.reader.classification import GcFileClass


@dataclass
class ContextData:
    spec_name: str = field(default="")
    head_cols: List[str] = field(default_factory=list)
    data_cols: List[str] = field(default_factory=list)
    first_row: Optional[int] = field(default=None)
    last_row: Optional[int] = field(default=None)
    header_format: str = field(default="")  # e.g. {header:}
    _data_dict: Dict[str, str] = field(default_factory=dict)
    # get sampling date & depth first for data

    @property
    def row_range(self) -> int:
        if not self.first_row or not self.last_row:
            return -1
        return self.last_row - self.first_row

    def set_data_dict(self, xl_reader: IExcelReader) -> None:
        if self._data_dict or isinstance(self, NoContextData):
            return
        if self.first_row is None or self.last_row is None:
            raise ValueError("Need to populate first row, last row and cols before reading data.")
        for row in range(self.first_row, self.last_row + 1):
            for head_col, data_col in zip(self.head_cols, self.data_cols):
                data_addr = ExcelAddress(f"{data_col}{row}")
                val = xl_reader.read_cell(data_addr)
                if has_value(val):
                    head_addr = ExcelAddress(f"{head_col}{row}")
                    raw_header = str(xl_reader.read_cell(head_addr)).strip()
                    if raw_header.endswith(":"):
                        self.header_format = "{header}:"
                    header = raw_header.replace(':', '').title()

                    if "depth" in header.lower():
                        val, unit = self.separate_text_and_number(val)
                        header = f"{header}<{unit}>"

                    if header.lower().startswith('lat') or header.lower().startswith('lon'):
                        val = self.convert_degrees_mins_secs_to_lat_lon(val)

                    self._data_dict[header] = val


    def get_data_dict(self) -> Dict[str, str]:
        if not self._data_dict:
            raise ValueError("Need to call set_data_dict(xl_reader) to populate internal state.")
        return self._data_dict

    @staticmethod
    def convert_degrees_mins_secs_to_lat_lon(coord: str) -> Any:
        try:
            return float(coord)
        except ValueError:
            try:
                deg_str, rest = coord.split("°")
                deg = float(deg_str.strip())
                parts = rest.split("'")
                mins = float(parts[0].strip())
                secs = float(parts[1].strip())
                return deg + (mins / 60) + (secs / 60 / 60)
            except ValueError:                
                return coord  # not a recognised degrees min, sec format

    @staticmethod
    def separate_text_and_number(val: str) -> Tuple[Optional[float], str]:
        num_str, text = "", ""
        for char in val:
            if char.isdigit() or char == ".":
                num_str += char
            elif char == " ":
                continue
            else:
                text += char
        if num_str:
            return float(num_str), text
        return None, text

    def get_any_depth(self) -> str:
        data = self.get_data_dict()
        if 'Top Depth' in data:
            return data['Top Depth']
        for head, val in data.items():
            head_fmt = str(head).lower().strip()
            if 'depth' in head_fmt:
                return val
        return ""

    def get_sample_type(self) -> str:
        for head, val in self.get_data_dict().items():
            head_fmt = str(head).lower().strip()
            if head_fmt.startswith('sam') and head_fmt.endswith('type'):
                return val
        return ""


@dataclass
class NoContextData(ContextData):
    pass
    

class IContextDataReader(ABC):
    @abstractmethod
    def get_context_data(self) -> ContextData:
        pass


@dataclass
class ContextDataSpec:
    name: str
    desc: str
    header_cols: List[str]
    data_cols: List[str]


spec_weat_v1 = ContextDataSpec(name="spec_weat_v1", desc="older Weatherford style files",
                               header_cols=["A", "AC"], data_cols=["H", "AM"])

spec_weat_v2 = ContextDataSpec(name="spec_weat_v2", desc="newer Weatherford style files",
                               header_cols=["A", "AD"], data_cols=["K", "AN"])


@dataclass
class WeatherfordStyleContextDataReader(IContextDataReader):
    _xl_reader: IExcelReader
    possible_specs: ClassVar[List[ContextDataSpec]] = [spec_weat_v1, spec_weat_v2]

    def get_context_data(self) -> ContextData:
        best_range = 0
        selected_context_data: ContextData = NoContextData()
        for spec in self.possible_specs:
            start_row, end_row = 0, 0
            for row in range(1,17):  # seen start between 2-3 and end 11-14 in this class (~20 examples)
                if not start_row:
                    if all([self._xl_reader.has_value(ExcelAddress(f"{col}{row}")) 
                            for col in spec.header_cols]):
                        start_row = row
                elif not end_row:
                    if all([not self._xl_reader.has_value(ExcelAddress(f"{col}{row}")) 
                            for col in spec.header_cols]):
                        end_row = row-1
                        break
            data = ContextData(head_cols=spec.header_cols,
                               data_cols=spec.data_cols,
                               first_row=start_row, last_row=end_row)
            if data.row_range > best_range:
                selected_context_data = data
        return selected_context_data


@dataclass
class NoContextDataReader(IContextDataReader):
    def get_context_data(self) -> ContextData:
        return NoContextData()


def get_context_data_reader(file_class: GcFileClass, xl_reader: IExcelReader) -> IContextDataReader:
    if file_class == GcFileClass.One:
        return WeatherfordStyleContextDataReader(_xl_reader = xl_reader)
    # TODO - throw NotImplementedError instead and handle at top level (to report back to client)
    return NoContextDataReader()  # no reader for other file classes yet
