# -*- coding: utf-8 -*-
'''
Created on 2020年11月25日
'''
import base64
import os
import math
import re
import threading

import platform

import requests
from k_parse_tool.lib.file_process_abstract_factory import FileProcessAbstractFactory

is_win_env = False
if platform.system().lower() == 'windows':
    is_win_env = True
    import win32com
    import win32com.client
    import pythoncom
# elif platform.system().lower() == 'linux':
#     import subprocess

from docx import Document
from pydocx import PyDocX


class WordFileProcessAbstractFactory():

    @staticmethod
    def get_word_file_process_object(word_file_type):
        lower_word_file_type = word_file_type.lower()
        if lower_word_file_type == 'docx':
            return PyDocXFileProcess()
        else:
            return PyDocFileProcess()


class PyDocXFileProcess(FileProcessAbstractFactory):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(PyDocXFileProcess, "_instance"):
            with PyDocXFileProcess._instance_lock:
                if not hasattr(PyDocXFileProcess, "_instance"):
                    PyDocXFileProcess._instance = object.__new__(cls)
        return PyDocXFileProcess._instance

    def process_file_content(self, file_path, files_process_api):
        result = ''
        try:
            docx = Document(file_path)
            for para in docx.paragraphs:
                line = para.text
                result = f'{result}\n{line}'
        except:
            pass
        return result

    @staticmethod
    def convert_file_to_html(file_path):
        html = PyDocX.to_html(file_path)
        return str(html)


class PyDocFileProcess(FileProcessAbstractFactory):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(PyDocFileProcess, "_instance"):
            with PyDocFileProcess._instance_lock:
                if not hasattr(PyDocFileProcess, "_instance"):
                    PyDocFileProcess._instance = object.__new__(cls)
        return PyDocFileProcess._instance

    def process_file_content(self, file_path, files_process_api):
        if is_win_env:
            # win环境
            return PyDocFileProcess.get_word_content_by_win32(file_path)
        else:
            return PyDocFileProcess.get_word_content_by_api(file_path, files_process_api)

    @staticmethod
    def get_word_content_by_win32(file_path):
        result = ''
        try:
            pythoncom.CoInitialize()
            ms_word = win32com.client.Dispatch("Word.Application")
            ms_word.Visible = 0  # 后台运行
            ms_word.DisplayAlerts = 0  # 不显示，不警告
            doc = ms_word.Documents.Open(file_path)
            for i in doc.Paragraphs:
                line = i.Range.Text
                result = f'{result}\n{line}'
            doc.Close()
            ms_word.Quit()
        except:
            pass
        return result

    # # 通过antiword提取到的word格式不对，暂时弃用
    # @staticmethod
    # def get_word_content_by_antiword(file_path):
    #     result = ''
    #     try:
    #         output = subprocess.check_output(["antiword", file_path])
    #         # 解码
    #         result = output.decode('utf8')
    #     except:
    #         pass
    #     return result

    @staticmethod
    def get_word_content_by_api(file_path, files_process_api):
        result = ''
        try:
            with open(file_path, 'rb') as f:
                base64_data = base64.b64encode(f.read())
                s = base64_data.decode()
                # print('word:word/doc;base64,%s' % s)
                data = {
                    'fileCode': str(s),
                    'fileSuffix': "doc"
                }
                response = requests.post(files_process_api, data=data)
                result = response.text
        except:
            pass
        return result

    def word_file_content_format(self, file_content):
        # 去除空行,去除行中仅有数字,行中仅有特殊字符
        if file_content is None or len(file_content.strip()) == 0: return ""
        file_content_line_array = file_content.split('\n')
        list = []
        count = 0
        result = ''
        for line in range(len(file_content_line_array)):
            line_value = file_content_line_array[line]
            if self.string_compiler(line_value, r"^\s*[\d\s]*?\s*$"): continue
            if self.string_compiler(line_value, r"^\s*第[\d\S]{0,3}页\s*$"): continue
            if self.string_compiler(line_value, r"^\s*第\d*页\s*，?\s*共\d*页\s*$"): continue
            if self.string_compiler(line_value,
                                    r"^\s*本?文书一式\s*.?\s*份[。，：]\s*?((其中)?.{0,2}\s*份[（）\s\u4e00-\u9fa5]{1,20}[，。]?\s*){1,}$"): continue
            list.append(line_value)
            count += len(line_value)
        avg = math.ceil(count / len(list))
        for i in range(len(list)):
            i_value = list[i].strip()
            sep = ''
            if len(i_value) < avg or self.string_compiler(i_value, r"^[\s\S]*?[：；。:;.）]$"):
                sep = '\n'
            result = f'{result}{i_value}{sep}'
        return result

    @staticmethod
    def convert_file_to_html(file_path,files_process_api=None):
        if is_win_env:
            # win环境
            word = win32com.client.Dispatch("Word.Application")
            doc = word.Documents.Open(file_path) # 绝对路径doc文件
            new_file_path = f'{file_path}x'
            doc.SaveAs(new_file_path, 16) # 保存的docx文件，绝对路径
            doc.Close()
            word.Quit()
            return PyDocXFileProcess.convert_file_to_html(new_file_path)
        else:
            return PyDocFileProcess.get_word_content_by_api(file_path, files_process_api)