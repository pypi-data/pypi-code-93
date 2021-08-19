from typing import Dict, Optional, List
from ezutils.files import writelines
import os
from enum import Enum


class SaveFormat(Enum):
    iOS = 1,
    Android = 2,
    Flutter = 3


class _StringFile:

    def __init__(self, column_title: str, filename_to_save: str):
        self.filename = filename_to_save
        self.column_title = column_title
        self.column_index = -1
        self.rows = []  # [[key1, value1],[key2, value2], ...]

    def update_column_index(self, title_row: List[str]):
        index = 0
        for title in title_row:
            if self.column_title == title:
                self.column_index = index
                return
            index += 1

    def add_row(self, key_of_row, value):
        if key_of_row == None or len(key_of_row) == 0:
            return

        self.rows.append([key_of_row, value])

    def save(self, format: SaveFormat):
        # print(f'saving:rows[{len(self.rows)}] {self.filename}')

        out_dir, filename = os.path.split(self.filename)
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        writelines(self._rows_to_save(format), self.filename)

    def _rows_to_save(self, format: SaveFormat):
        if format == SaveFormat.iOS:
            rows_to_save = ["// AUTO-GENERATED"]
            rows_to_save.extend(
                list(map(lambda row: f"{row[0]} = {row[1]};", self.rows))
            )
            return rows_to_save

        if format == SaveFormat.Android:
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

        if format == SaveFormat.Flutter:
            rows_to_save = ['{']
            rows_to_save.extend(
                list(map(lambda row: f'    "{row[0]}":"{row[1]}",', self.rows)))
            rows_to_save.extend(
                ['}']
            )
            return rows_to_save

        ex = Exception('Not supported')
        raise ex
