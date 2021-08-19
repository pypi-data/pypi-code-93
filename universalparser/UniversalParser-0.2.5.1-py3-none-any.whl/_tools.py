from typing import Dict, List
from functools import reduce
from zipfile import ZipFile
import subprocess
from ._exception import *
import re

def __intersection(obj1, obj2):
    result = []
    for _1 in obj1:
        for _2 in obj2:
            if _1 == _2:
                result.append(_1)
                break
    return result

def find_intersection(datas: List[List[int]]) -> List[int]:
    return list(reduce(__intersection, datas))

def patt_template_replace(data: str, *args, patt=None, **kwargs):
    if patt is None:
        patt = re.compile(r'\$\{(.+?)\}')
    def deal(x):
        if x.group(1) in kwargs:
            return kwargs[x.group(1)]
        else:
            return x.group(0)
    if patt.search(data):
        return patt.sub(deal, data)
    else:
        return data

def read_content_from_zip(
        zip_file_path: str
        , read_file_path: str='word/document.xml'
        , encoding: str='utf-8'
    ) -> str:
    try:
        with ZipFile(zip_file_path) as zip_obj:
            with zip_obj.open(read_file_path) as op_file:
                content = op_file.read().decode(encoding)
    except Exception as e:
        raise ZipParseError(f'zip-file can not be parsed.{e}')

    return content

def read_content_from_zipobj(
        zip_obj
        , read_file_path: str='word/document.xml'
        , encoding: str='utf-8'
    ):
    try:
        with zip_obj.open(read_file_path) as op_file:
            content = op_file.read().decode(encoding)
    except Exception as e:
        raise ZipParseError(f'zip-file can not be parsed.{e}')

    return content

# def save_modify_content_to_zip(
#         zip_file_path: str
#         , new_text: str
#         , modify_file_path: str='word/document.xml'
#         , encoding: str = 'utf-8'
#     ):
#     raise ZipParseError('Not supported at the moment.')
#     with ZipFile(zip_file_path, 'a') as zip_obj:
#         # zip_obj.writestr(modify_file_path, (new_text).encode(encoding))
#         with zip_obj.open(modify_file_path, mode='w', force_zip64=True) as fp:
#             fp.write((new_text).encode(encoding))

# def save_modify_content_to_zipobj(
#         zip_obj: ZipFile
#         , new_text: str
#         , modify_file_path: str='word/document.xml'
#         , encoding: str = 'utf-8'
#     ):
#     raise ZipParseError('Not supported at the moment.')
#     try:
#         zip_obj.writestr(modify_file_path, (new_text).encode(encoding))
#     except Exception as e:
#         raise ZipParseError(f'file not exists.{e}')

def save_docs_with_modify_by_move(
        zip_obj: ZipFile
        , modify_files: Dict[str, str] # {'word/document.xml': '...', ...}
        , save_zip_path: str = 'output.docx'
        # , encoding: str = 'utf-8'
    ):
    out_zip_obj = ZipFile(save_zip_path, 'w')
    for item in zip_obj.infolist():
        if item.filename in modify_files:
            out_zip_obj.writestr(item, modify_files[item.filename])
        else:
            buffer = zip_obj.read(item.filename)
            out_zip_obj.writestr(item, buffer)
    out_zip_obj.close()
