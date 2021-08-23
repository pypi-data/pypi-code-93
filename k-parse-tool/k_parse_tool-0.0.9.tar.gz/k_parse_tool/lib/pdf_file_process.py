# -*- coding: utf-8 -*-
'''
Created on 2020年11月25日
'''
import math
import re
import threading

import pdfplumber
from enum import Enum

from k_parse_tool.lib.file_process_abstract_factory import FileProcessAbstractFactory


class PdfFileProcessAbstractFactory():
    pdf_lib_type = Enum("pdf_lib_type", ("pdfplumber", "pdfminer"))

    @staticmethod
    def get_pdf_file_process_object(pdf_lib_type):
        if PdfFileProcessAbstractFactory.pdf_lib_type.pdfplumber == pdf_lib_type:
            return PdfplumbePdfFileProcess()
        else:
            pass

    @staticmethod
    def string_compiler(str_input, regex, re_flag=re.I):
        text = re.compile(regex, re_flag)
        if text.match(str_input):
            return True
        else:
            return False

    @staticmethod
    def pdf_file_content_format(file_content):
        # 去除空行,去除行中仅有数字,行中仅有特殊字符
        if file_content is None or len(file_content.strip()) == 0: return ""
        file_content_line_array = file_content.split('\n')
        list = []
        count = 0
        result = ''
        for line in range(len(file_content_line_array)):
            line_value = file_content_line_array[line]
            list.append(line_value)
            count += len(line_value.strip())
        avg = math.ceil(count / len(list))
        for i in range(len(list)):
            i_value = ''.join(list[i].split())
            if PdfFileProcessAbstractFactory.string_compiler(i_value, r"^[\s—]*[\d\s]*?[\s—]*$"): continue
            if PdfFileProcessAbstractFactory.string_compiler(i_value, r"^\s*第[\d\S]{0,3}页\s*$"): continue
            if PdfFileProcessAbstractFactory.string_compiler(i_value, r"^\s*第\d*页\s*，?\s*共\d*页\s*$"): continue
            if PdfFileProcessAbstractFactory.string_compiler(i_value,
                                    r"^\s*本?文书一式\s*.?\s*份[。，：]\s*?((其中)?.{0,2}\s*份[（）\s\u4e00-\u9fa5]{1,20}[，。]?\s*){1,}$"): continue
            sep = ''
            if len(i_value) < avg or PdfFileProcessAbstractFactory.string_compiler(i_value, r"^[\s\S]*?([：；。:;.）]+|[\da-z]{5,})$", re.I):
                sep = '\n'
            result = f'{result}{i_value}{sep}'
        return result


class PdfplumbePdfFileProcess(FileProcessAbstractFactory):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(PdfplumbePdfFileProcess, "_instance"):
            with PdfplumbePdfFileProcess._instance_lock:
                if not hasattr(PdfplumbePdfFileProcess, "_instance"):
                    PdfplumbePdfFileProcess._instance = object.__new__(cls)
        return PdfplumbePdfFileProcess._instance

    def process_file_content(self, file_path, files_process_api):
        content = ''
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_content = page.extract_text()
                if page_content is not None and len(page_content) > 0:
                    content = f'{content}{page_content.strip()}\n'
                # page.extract_tables(table_settings={})  # 提取表格
                # print(content)
        return content
