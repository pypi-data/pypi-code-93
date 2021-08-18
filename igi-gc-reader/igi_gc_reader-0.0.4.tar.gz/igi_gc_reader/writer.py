from typing import List

import openpyxl

from igi_gc_reader.reader.gc_reader import GcSheet
from igi_gc_reader.sample_data import SampleData
from igi_gc_reader.reader.excel_address import col_index_to_letter


def write_sheets(gc_sheets: List[GcSheet], out_path: str):
    wb = openpyxl.Workbook()

    for idx, gc in enumerate(gc_sheets):
        # starting out with 1 sheet out per sheet in - can comb later if required
        sh = wb.create_sheet(index=idx, title=gc.sheet_name)
        sample_data = SampleData(gc.page_data, igi_analysis=gc.get_igi_analysis())

        context_dict = gc.context_data.get_data_dict()
        value_row = sample_data.n_header_rows + 1
        for col_idx, (header, value) in enumerate(context_dict.items()):
            col = col_index_to_letter(col_idx)
            sh[f"{col}1"] = header
            sh[f"{col}{value_row}"] = value

        for col_idx, (headers, value) in enumerate(zip(sample_data.get_headers(),
                                                       sample_data.get_sample_row()), 
                                                   start=col_idx+1):
            col = col_index_to_letter(col_idx)
            header_row_1, header_row_2 = headers[0], headers[1]
            sh[f"{col}1"] = header_row_1
            if header_row_2 is None:
                sh[f"{col}2"] = value
            else:                
                sh[f"{col}2"] = header_row_2
                sh[f"{col}3"] = value

    wb.save(out_path)
