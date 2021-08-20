# -*- coding: UTF-8 -*-
# @Time    : 2020/10/22
# @Author  : xiangyuejia@qq.com
from aitool.basic_function.basic import split_dict

from aitool.basic_function.file import file_exist as file_exist
from aitool.basic_function.file import dump_json as dump_json
from aitool.basic_function.file import load_json as load_json
from aitool.basic_function.file import dump_pickle as dump_pickle
from aitool.basic_function.file import load_pickle as load_pickle
from aitool.basic_function.file import dump_lines as dump_lines
from aitool.basic_function.file import load_lines as load_line
from aitool.basic_function.file import load_lines as load_lines
from aitool.basic_function.file import dump_excel as dump_excel
from aitool.basic_function.file import load_excel as load_excel
from aitool.basic_function.file import dump_csv as dump_csv
from aitool.basic_function.file import load_csv as load_csv

from aitool.basic_function.file import download_file as download_file
from aitool.basic_function.file import zip as zip
from aitool.basic_function.file import unzip as unzip
from aitool.basic_function.file import prepare_data as prepare_data

from aitool.basic_function.format_data import flatten as flatten

from aitool.basic_function.singleton import singleton as singleton
from aitool.basic_function.exe_time import exe_time as exe_time
from aitool.basic_function.retry import retry
from aitool.basic_function.time import timeout
from aitool.basic_function.time import timestamp

from aitool.basic_function.cache import cache

from aitool.task_customized.ip_enhance.filter import has_family_name
from aitool.task_customized.ip_enhance.filter import is_common_word
from aitool.task_customized.ip_enhance.filter import is_relationship_title
from aitool.task_customized.ip_enhance.filter import is_contains_english
from aitool.task_customized.ip_enhance.filter import cut_until_char
from aitool.task_customized.ip_enhance.filter import delete_char
from aitool.task_customized.ip_enhance.filter import is_nick_name
from aitool.task_customized.ip_enhance.filter import is_contains_figure
from aitool.task_customized.ip_enhance.filter import delete_age_describe
from aitool.task_customized.ip_enhance.filter import is_contains_chinese
from aitool.task_customized.ip_enhance.filter import is_all_chinese
from aitool.task_customized.ip_enhance.filter import is_black_name
from aitool.task_customized.ip_enhance.filter import clean_role
from aitool.task_customized.ip_enhance.filter import clean_alias
from aitool.task_customized.ip_enhance.filter import delete_nested_text
from aitool.task_customized.ip_enhance.filter import select_nested_text
from aitool.task_customized.ip_enhance.filter import is_sub_ip
from aitool.task_customized.ip_enhance.filter import get_core_ip
