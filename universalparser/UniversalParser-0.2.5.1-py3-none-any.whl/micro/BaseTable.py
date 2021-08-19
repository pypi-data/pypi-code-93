# from abc import ABC, abstractmethod
from typing import Tuple
from .templates import parse_html_table
from UniversalParser._exception import *
from UniversalParser.manager import ChainManager
import xlwt

class WordTag:
    TBL = 'w:tbl'
    TR = 'w:tr'
    TC = 'w:tc'
    P = 'w:p'
    R = 'w:r'
    T = 'w:t'

class PowerPointTag:
    ...

class ExcelTag:
    ...

class BaseTable:

    def __init__(self, manager: ChainManager, tag_type: str='word') -> None:
        super().__init__()
        self.manager = manager
        self.Tag = self.__get_tag_type(tag_type)

        self.tables = []
        self.refresh_tables()

    def __get_tag_type(self, tag_type: str='word'):
        if 'word' == tag_type:
            return WordTag
        elif 'ppt' == tag_type:
            return PowerPointTag
        elif 'excel' == tag_type:
            return ExcelTag
        else:
            raise Exception('Not exists.')

    def refresh_tables(self):
        self.tables = []
        for w_tbl in self.manager.find_nodes_by_tag(
                self.Tag.TBL
            ):
            table = []
            for w_tr in self.manager.find_nodes_with_ancestor(
                    w_tbl
                    , tag_ = self.Tag.TR
                ):
                row = []
                for w_tc in self.manager.find_nodes_with_ancestor(
                        w_tr
                        , tag_ = self.Tag.TC
                    ):
                    try:
                        row.append(
                            self.manager.find_text(
                                w_tc[self.Tag.P][self.Tag.R][self.Tag.T]
                            )
                        )
                    except:
                        row.append('')
                table.append(row)
            self.tables.append(table)
        return self.tables

    def modify_cell_by_coordinate(self, table_loc: int, coordinate: Tuple[int, int], new_value) -> str:
        row, col = coordinate
        try:
            table = self.manager.find_nodes_by_tag(self.Tag.TBL)[table_loc-1]
            row_obj = self.manager.find_nodes_with_ancestor(table, tag_ = self.Tag.TR)[row-1]
            cell_obj = self.manager.find_nodes_with_ancestor(row_obj, tag_ = self.Tag.TC)[col-1]
            old_value = self.manager.update_text(cell_obj[self.Tag.P][self.Tag.R][self.Tag.T], new_value)
        except Exception as e:
            raise ZipParseError(f'Modify zip-file error.{e}')
        else:
            return old_value

    def modify_cell_by_template(self, row_feature: str, col: int, new_value) -> str:
        ...

    def batch_modify_cells(self):
        ...

    def to_html(self
            , title: str='Table'
            , out_path: str='tables.html'
            , encoding: str='utf-8'
        ):
        with open(out_path, 'w', encoding=encoding) as fp:
            fp.write(parse_html_table(self.tables, title=title))

    def to_word(self): pass

    def to_pdf(self): pass        

    def to_excel(self
            , file_path: str = 'tables.xls'
            , sheet_name: str = 'Sheet1'
            , encoding: str = 'utf-8'
        ):
        workbook = xlwt.Workbook(encoding)
        worksheet = workbook.add_sheet(sheet_name)
        offset = 0
        for table in self.tables:
            for row_index, row in enumerate(table):
                for col_index, value in enumerate(row):
                    try:
                        worksheet.write(row_index+offset, col_index, float(value))
                    except:
                        worksheet.write(row_index+offset, col_index, value)
            else:
                offset += row_index + 1
        workbook.save(file_path)
