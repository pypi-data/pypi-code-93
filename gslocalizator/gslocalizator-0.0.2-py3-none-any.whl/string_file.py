from typing import Dict, Optional, List
from ezutils.files import writelines
import os


class _StringFile:

    def __init__(self, column_title: str, filename_to_save: str):
        self.filename = filename_to_save
        self.column_title = column_title
        self.column_index = -1
        self.rows = []  # [[key1, value1],[key2, value2], ...]

    def update_column_index(self, title_row: List[str], key_col_idx: int):
        index = 0
        title_without_key = []
        title_without_key.extend(title_row[:key_col_idx])
        title_without_key.extend(title_row[key_col_idx+1:])

        for title in title_without_key:
            if self.column_title == title:
                self.column_index = index
                return
            index += 1

    def add_row(self, key_of_row, value):
        if key_of_row == None or len(key_of_row) == 0:
            return

        self.rows.append([key_of_row, value])

    def save(self, format: str):
        out_dir, filename = os.path.split(self.filename)
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        print(f'{len(self.rows)} records -> {self.filename}')
        writelines(self._rows_to_save(format), self.filename)

    def _rows_to_save(self, format: str):
        if format == "iOS":
            rows_to_save = ["// AUTO-GENERATED"]
            rows_to_save.extend(
                list(
                    map(lambda row: f'"{row[0]}" = "{row[1]}";', self.rows))
            )
            return rows_to_save

        if format == "Android":
            rows_to_save = [
                '<?xml version="1.0" encoding="utf-8"?>', '', '<resources>']
            rows_to_save.extend(
                list(
                    map(lambda row: f'<string name="{row[0]}">{row[1]}</string>', self.rows))
            )
            rows_to_save.extend(
                ['</resources>']
            )
            return rows_to_save

        if format == "Flutter":
            rows_to_save = ['{']
            rows_to_save.extend(
                list(map(lambda row: f'    "{row[0]}":"{row[1]}",', self.rows)))
            rows_to_save.extend(
                ['}']
            )
            return rows_to_save

        ex = Exception('Not supported')
        raise ex
