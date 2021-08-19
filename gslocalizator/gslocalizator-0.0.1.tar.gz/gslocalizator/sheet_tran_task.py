
from typing import Dict, Optional, List
from gslocalizator.string_file import SaveFormat, _StringFile


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
                 exclude_headers: Optional[str] = []):

        self.from_sheet_range = from_sheet_range
        self.sheet_name = get_sheetname_from_range(from_sheet_range)
        self.from_value_column_to_file = from_value_column_to_file
        self.with_key_column = with_key_column
        self.exclude_headers = exclude_headers
        self.string_files = self._init_files(from_value_column_to_file)

    def _init_files(self, from_value_column_to_file: Dict[str, str]) -> List[_StringFile]:

        files = []
        for column_title, filename_to_save in from_value_column_to_file.items():
            files.append(_StringFile(column_title, filename_to_save))
        return files

    def is_my_sheet_range(self, range_in: str) -> bool:
        sheet_name_in = get_sheetname_from_range(range_in)
        return sheet_name_in == self.sheet_name

    def update_rows(self, rows: List[List[str]]):

        if rows == None or len(rows) == 0:
            return

        titleRow = rows[0]
        if titleRow == None or len(titleRow) == 0:
            return

        for stringfile in self.string_files:
            stringfile.update_column_index(titleRow)

        key_col_idx = 0
        if self.with_key_column != None and len(self.with_key_column) > 0:
            key_col_idx = self._find_key_index(titleRow)

        for row in rows[1:]:
            keyOfRow = row[key_col_idx]
            self._update_row(keyOfRow, row)

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

        for exhr in self.exclude_headers:
            if key_of_row.find(exhr) == 0:  # start with exhr
                return

        for string_file in self.string_files:
            value = row[string_file.column_index]
            string_file.add_row(key_of_row, value)

    def save(self, format: SaveFormat):
        for string_file in self.string_files:
            string_file.save(format)
