# -*- coding: utf-8 -*-
'''
Created on 2020年11月07日
'''

import abc
import re


class FileProcessAbstractFactory(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process_file_content(self, file_path, files_process_api):
        raise NotImplementedError("Must implement process_file_content")

    # 字符串验证
    def string_compiler(self, str, regex, re_flag=re.I):
        text = re.compile(regex, re_flag)
        if text.match(str):
            return True
        else:
            return False
