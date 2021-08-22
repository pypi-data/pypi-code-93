from __future__ import annotations

from typing import TYPE_CHECKING, Union

import openpyxl
import pandas as pd
import pandas.io.formats.excel
from pandas.io.excel._openpyxl import OpenpyxlWriter  # NoQA

if TYPE_CHECKING:
    from pathlib import Path

# Override pandas excel styles
# fmt: off
class ExcelFormatterNoStyles(pandas.io.formats.excel.ExcelFormatter): header_style = None  # NoQA
pandas.io.formats.excel.ExcelFormatter = ExcelFormatterNoStyles  # NoQA
# fmt: on


def excel_interface(filename: Path) -> pd.ExcelWriter:
    # try to open an existing workbook
    book = openpyxl.load_workbook(filename)
    # create writer
    writer = OpenpyxlWriter(filename, datetime_format="DD/MM/YYYY")
    # patch in loaded workbook, copy existing sheets
    writer.book = book
    writer.sheets = {ws.title: ws for ws in book.worksheets}

    return writer


def write_to_workbook(
        writer: pd.ExcelWriter,
        df: pd.DataFrame,
        sheet_name: str,
        start_row: int,
        hidden_columns: dict = None,
        df_to_excel_kwargs: dict[str, object] = None,
):
    df.to_excel(writer, sheet_name, startrow=start_row, **(df_to_excel_kwargs | {"engine": None}))

    # if hidden_columns is not None and sheet_name in hidden_columns:
    #     ws = writer.sheets[sheet_name]
    #     for col in hidden_columns[sheet_name]:
    #         ws.column_dimensions[openpyxl.utils.get_column_letter(col)].hidden = 1
