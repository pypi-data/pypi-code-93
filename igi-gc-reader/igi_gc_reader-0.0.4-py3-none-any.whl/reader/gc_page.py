from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, ClassVar, DefaultDict, Dict, Iterator, List, Tuple, Set
from abc import ABC, abstractmethod
from enum import Enum

from igi_gc_reader.reader.excel_address import ExcelAddress, col_index_to_letter, col_letter_to_index
from igi_gc_reader.reader.excel_reader import IExcelReader, has_value
from igi_gc_reader.reader.classification import GcFileClass


@dataclass
class GcPage:
    page_no: int
    headers: List[str] = field(default_factory=list)
    data_rows: List[List[Any]] = field(default_factory=list)

    def has_data(self) -> bool:
        return any(self.data_rows)


@dataclass  # type: ignore
class IGcPageReader(ABC):
    _xl_reader: IExcelReader

    @abstractmethod
    def get_pages(self) -> Iterator[GcPage]:
        pass


class PagePhase(Enum):
    Seeking = 1
    InPageMetadata = 2
    BetweenMetadataAndHeaders = 3
    InPageHeaders = 4
    InPageData = 5


# TODO - *** Future note for classifier ***
#        distinguishing characteristic of this file class seems to be 🤞 the repeating metadata
#        blocks at the top of each page - looking for any of 4 specific headers usually seen in 
#        left metadata column. This could be a useful test when implementing a better classifier!

# TODO - this is an early stage experiment. If keeping consider changing to a pattern where 
#        we have an IPageState abstract class and a subclass for each state:

# IPageState(xl_reader, page_data):
#   def transition(row) -> phase  # switch to alt state if transition criteria is detected
#   def process(row)

# then just go through states for each row and call transition (and process if no transition)
@dataclass
class GcPageClassOneReader(IGcPageReader):
    _xl_reader: IExcelReader
    header_cols: List[str] = field(default_factory=list)  # assume data uses same cols for now
    expected_metadata_headers: ClassVar[Set[str]] = {'Company:', 'Well Name:', 'Depth:', 
                                                      'Sampling Point:'}
    page_start_col: ClassVar[str] = 'A'
    derived_data_header: ClassVar[str] = 'Miscellaneous Ratios'  # use as an indicator to stop
    start_page_search_from_row: ClassVar[int] = 40
    max_cols: ClassVar[int] = 60  # look for headers in all columns up to this
    end_after_n_empty_rows: ClassVar[int] = 100
    n_empty_cols_for_row: ClassVar[int] = 10  # treat the row as empty if first n cols are
    max_rows: ClassVar[int] = 3000  # ensure an error doesn't lead to infinite loop!

    def get_pages(self) -> Iterator[GcPage]:
        # TODO - p3 tmp could add build page method and call until StopIteration
        #        would solve problem of having to reset local state (+ instance state)
        #        for each page. Worth it if eventually moving to state machine pattern?
        found_start = False  # not unique to each page (set once for all)
        page_no = 1
        consecutive_empty_rows = 0
        header_row_num = 0
        phase = PagePhase.Seeking
        current_page = GcPage(page_no)
        header_col_to_values: DefaultDict[str, List[str]] = defaultdict(list)
        data_row_col_pair_to_value: Dict[Tuple[int, str], Any] = {}

        # 3 stopping conditions as of 05/07/2021:
        #   1) Hit >= n empty rows consecutively (after finding start of data pages)
        #      (n configured as ClassVar with {n_empty_cols_for_row})
        #   2) Detected a derived data header (derived data incl at end). This is 
        #      a backup for in case there is not a large gap from end of last data page
        #      (derived data header configured as ClassVar: {derived_data_header})
        #   3) Fallback - set a max num rows just incase of a logical error or unexpected
        #      file format to prevent possible infinite loop.
        #      (max rows configured as ClassVar: {max_rows})
        for row in range(self.start_page_search_from_row, self.max_rows):
            is_empty_row = self.is_empty_row(row)
            consecutive_empty_rows = 0 if not is_empty_row else consecutive_empty_rows + 1

            if consecutive_empty_rows >= self.end_after_n_empty_rows and found_start:
                if current_page.has_data():
                    yield current_page
                break

            # phase 1
            if phase == PagePhase.Seeking:
                if self.is_start_of_new_page(row):
                    found_start = True
                    phase = PagePhase.InPageMetadata

            # phase 2
            if phase == PagePhase.InPageMetadata:
                if is_empty_row:
                    phase = PagePhase.BetweenMetadataAndHeaders

            # phase 3
            if phase == PagePhase.BetweenMetadataAndHeaders:
                if not is_empty_row:
                    phase = PagePhase.InPageHeaders
                    header_row_num = 1

            # phase 4
            if phase == PagePhase.InPageHeaders:
                if header_row_num <3:
                    for col, val in self.get_col_value_pairs(row):
                        header_col_to_values[col].append(str(val))
                        if val == self.derived_data_header:
                            return  # we are into derived data - last data page already returned
                    header_row_num += 1  
                else:
                    phase = PagePhase.InPageData

                    # add headers to current page (all values for each col to handle multi row)
                    for col, values in sorted(header_col_to_values.items(), 
                                              key=lambda kvp: col_letter_to_index(kvp[0])):
                        header = " ".join(values)
                        current_page.headers.append(header)

                    header_row_num = 0  # reset
                    header_col_to_values = defaultdict(list)  # reset

            # phase 5
            if phase == PagePhase.InPageData:
                is_new_page = self.is_start_of_new_page(row) 
                if is_new_page or is_empty_row:
                    if is_new_page:
                        phase = PagePhase.InPageMetadata
                    else:
                        phase = PagePhase.Seeking

                    self.add_data_rows(current_page, data_row_col_pair_to_value)

                    # return current page
                    yield current_page
                    page_no += 1
                    current_page = GcPage(page_no)  # reset
                    data_row_col_pair_to_value = {}  # reset
                    continue

                for col, val in self.get_col_value_pairs(row):
                    data_row_col_pair_to_value[(row, col)] = val

    def is_empty_row(self, row:int):
        check_cols = [col_index_to_letter(i) for i in range(0, self.n_empty_cols_for_row)]
        return not any(has_value(self.read(col, row)) for col in check_cols)

    def read(self, col: str, row: int) -> Any:
        return self._xl_reader.read_cell(ExcelAddress(f"{col}{row}"))

    def is_start_of_new_page(self, row) -> bool:
        col_a_cleaned = str(self.read(col=self.page_start_col, row=row)).strip()
        return col_a_cleaned in self.expected_metadata_headers

    def get_col_value_pairs(self, row: int) -> Iterator[Tuple[str, Any]]:
        for col_idx in range(self.max_cols):
            col = col_index_to_letter(col_idx)
            val = self.read(col, row)
            if has_value(val):
                yield col, val

    def add_data_rows(self, page: GcPage, 
                      data_row_col_pair_to_value: Dict[Tuple[int, str], Any]) -> None:
        cols = set([c for _, c in data_row_col_pair_to_value.keys()])
        ordered_cols = sorted(cols, key=lambda col: col_letter_to_index(col))
        ordered_rows = sorted(set([r for r, _ in data_row_col_pair_to_value.keys()]))
        for r in ordered_rows:
            data_row = []
            for c in ordered_cols:
                # need to incl empties so that data lines up with headers
                # TODO: Still some risk of misalignment e.g. if one col has no values
                #       the trouble is that the header cols don't align with the values
                #       precisely (e.g. val is merged group starting one col before header col)
                #       If we get issue above could match val cols to head cols by proximity 😩
                val = data_row_col_pair_to_value.get((r, c))
                data_row.append(val)
            page.data_rows.append(data_row)
            


def get_page_reader(xl_reader: IExcelReader, file_class: GcFileClass):
    if file_class == GcFileClass.One:
        return GcPageClassOneReader(xl_reader)
    raise NotImplementedError()


@dataclass
class GcPageData:
    """Combines individual pages."""
    pages: List[GcPage]

    def get_headers(self) -> List[str]:
        first_headers = self.pages[0].headers
        for other_page in self.pages[1:]:
            if other_page.headers != first_headers:
                raise ValueError(f"Expected all headers to be the same, but page "
                                 f"{other_page.page_no} has different headers to the first page. "
                                 f"Page {other_page.page_no}: {other_page.headers}, first page: "
                                 f"{first_headers}.")
        return first_headers

    def get_data(self) -> Iterator[List[Any]]:
        for page in self.pages:
            for row in page.data_rows:
                yield row            


def get_page_data(xl_reader: IExcelReader, file_class: GcFileClass) -> GcPageData:
    if file_class == GcFileClass.One:
        page_reader = GcPageClassOneReader(xl_reader)
        pages = list(page_reader.get_pages())
        if not pages:
            raise StopIteration("No page data found for file.")
        return GcPageData(pages)
    raise NotImplementedError()
