from dataclasses import dataclass, field
from typing import Iterator

from igi_gc_reader.reader.gc_page import GcPageData, get_page_data
from igi_gc_reader.reader.excel_reader import get_excel_reader, IExcelReader
from igi_gc_reader.reader.context_data import ContextData, get_context_data_reader
from igi_gc_reader.reader.classification import ( 
    GcFileClass, class_to_expected_analysis_addr, is_an_analysis)


@dataclass
class GcSheet:
    _xl_reader: IExcelReader
    sheet_name: str
    analysis: str = field(init=False, default="")
    analysis_addr: str = field(init=False, default="")
    file_class: GcFileClass = field(init=False, default=GcFileClass.Unclassified)
    context_data: ContextData = field(init=False, default_factory=ContextData)
    page_data: GcPageData = field(init=False)

    def __post_init__(self):
        self._set_analysis_and_class()
        context_data_reader = get_context_data_reader(self.file_class, self._xl_reader)
        self.context_data = context_data_reader.get_context_data()
        self.context_data.set_data_dict(self._xl_reader)
        try:
            self._set_page_data()
        except NotImplementedError:
            pass

    def get_igi_analysis(self):
        """Map from raw analysis text in the sheet to the IGI analysis group."""
        raw_analysis = self.analysis.lower()
        if "sat" in raw_analysis:
            return "Sat-GCMS" if "gcms" in raw_analysis else "Sat-GC"
        if "aro" in raw_analysis: 
            return "Arom-GCMS" if "gcms" in raw_analysis else "Arom-GC"
        return "WO-GCMS" if "gcms" in raw_analysis else "WO-GC"

    def _set_page_data(self):
        self.page_data = get_page_data(self._xl_reader, self.file_class)

    def _set_analysis_and_class(self) -> None:
        for file_class, expected_anal_addresses in class_to_expected_analysis_addr.items():
            for addr in expected_anal_addresses:
                potential_anal_val = self._xl_reader.read_cell(addr)
                if potential_anal_val and is_an_analysis(potential_anal_val):
                    self.file_class = file_class
                    self.analysis = potential_anal_val
                    self.analysis_addr = str(addr)
                    return

    def close(self):
        # TODO:p2 - consider making this and ExcelReader classes context managers
        self._xl_reader.close()
        del self._xl_reader


def get_gc_sheets(wb_path: str) -> Iterator[GcSheet]:
    xl_reader = get_excel_reader(wb_path)
    for sheet in xl_reader.get_sheet_names():
        # TODO: ** change approach - this assumes that we finish with 1 sheet then start with 
        #       next if we tried to get page data on prev sheet it would be wrong! Too fragile.
        xl_reader.set_sheet(sheet)
        yield GcSheet(xl_reader, sheet)


def get_gc_sheet(wb_path: str, sheet: str) -> GcSheet:
    xl_reader = get_excel_reader(wb_path, sheet)
    return GcSheet(xl_reader, sheet)
