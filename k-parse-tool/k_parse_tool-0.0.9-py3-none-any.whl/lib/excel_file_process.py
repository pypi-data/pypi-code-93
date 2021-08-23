# -*- coding: utf-8 -*-
'''
Created on 2020年11月25日
'''
import math
import re
import threading

from enum import Enum

from k_parse_tool.lib.file_process_abstract_factory import FileProcessAbstractFactory


class ExcelFileProcessAbstractFactory():
    excel_lib_type = Enum("excel_lib_type", ("Pandas", "xlrd_xlwt_xlutils", "openpyxl"))

    @staticmethod
    def get_excel_file_process_object(pdf_lib_type):
        if ExcelFileProcessAbstractFactory.excel_lib_type.Pandas == pdf_lib_type:
            return PandasExcelFileProcess()
        else:
            pass


class PandasExcelFileProcess(FileProcessAbstractFactory):

    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(PandasExcelFileProcess, "_instance"):
            with PandasExcelFileProcess._instance_lock:
                if not hasattr(PandasExcelFileProcess, "_instance"):
                    PandasExcelFileProcess._instance = object.__new__(cls)
        return PandasExcelFileProcess._instance

    def process_file_content(self, file_path):
        raise NotImplementedError("Must implement process_file_content")


    # 字符串验证
    def string_compiler(self, str,regex):
        text = re.compile(regex)
        if text.match(str):
            return True
        else:
            return False


