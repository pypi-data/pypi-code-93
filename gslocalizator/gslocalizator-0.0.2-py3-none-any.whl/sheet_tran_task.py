
from typing import Callable, Dict, Optional, List
from gslocalizator.string_file import _StringFile


def get_sheetname_from_range(from_sheet_range: str) -> str:
    if from_sheet_range == None:
        return None

    strings = from_sheet_range.split('!')
    if len(strings) < 1:
        return None

    name = strings[0]
    if len(name) == 0:
        return None
    return name


class _SheetTranTask:

    def __init__(self, from_sheet_range: str,
                 from_value_column_to_file: Dict[str, str],
                 with_key_column: Optional[str] = '',
                 exclude_headers: Optional[str] = [],
                 cell_formater: Optional[Callable[[str], str]] = (lambda s: s)):

        self.from_sheet_range = from_sheet_range
        self.sheet_name = get_sheetname_from_range(from_sheet_range)
        self.from_value_column_to_file = from_value_column_to_file
        self.with_key_column = with_key_column
        self.exclude_headers = exclude_headers
        self.cell_formater = cell_formater
        self.string_files = self._init_files(from_value_column_to_file)

    def _init_files(self, from_value_column_to_file: Dict[str, str]) -> List[_StringFile]:

        files = []
        for column_title, filename_to_save in from_value_column_to_file.items():
            files.append(_StringFile(column_title, filename_to_save))
        return files

    def is_my_sheet_range(self, range_in: str) -> bool:
        sheet_name_in = get_sheetname_from_range(range_in)
        return sheet_name_in == self.sheet_name

    def _fmt_cells_as_str(self, rows: List[List]):
        return list(
            map(lambda r: list(map(lambda c: self.cell_formater(f'{c}'), r)), rows))

    def update_rows(self, rows_raw: List[List]):

        if rows_raw == None or len(rows_raw) == 0:
            return

        rows = self._fmt_cells_as_str(rows_raw)

        title_row = rows[0]
        if title_row == None or len(title_row) <= 2:
            return

        key_col_idx = 0
        if self.with_key_column != None and len(self.with_key_column) > 0:
            key_col_idx = self._find_key_index(title_row)

        for stringfile in self.string_files:
            stringfile.update_column_index(title_row, key_col_idx)

        for values_row in rows[1:]:
            if values_row == None or len(values_row) < key_col_idx+1:
                continue

            key_of_row = values_row[key_col_idx]
            new_row = []
            new_row.extend(values_row[:key_col_idx])
            new_row.extend(values_row[key_col_idx+1:])
            self._update_row(key_of_row, new_row)

    def get_sheetname_from_range(self):
        return self.sheet_name

    def _find_key_index(self, titleRow: List[str]) -> int:

        index = 0

        for title in titleRow:
            if self.with_key_column == title:
                return index
            index += 1

        return 0

    def _update_row(self, key_of_row: str, row: List[str]):
        if key_of_row == None or len(key_of_row) == 0:
            return

        if row == None or len(row) == 0:
            return

        for exhr in self.exclude_headers:
            if key_of_row.find(exhr) == 0:  # start with exhr
                return
        for string_file in self.string_files:
            if len(row) < string_file.column_index + 1:
                string_file.add_row(key_of_row, "")
                continue
            value = row[string_file.column_index]
            string_file.add_row(key_of_row, value)

    def save(self, format: str):
        for string_file in self.string_files:
            string_file.save(format)
