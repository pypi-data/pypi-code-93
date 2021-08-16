# coding: utf-8
import os
import sys
import traceback
from pathlib import Path

"""
路径类
命名规则：
第一个abs/rel 用来表示是获取绝对路径还是相对路径的
第二个开始表示该方法的作用/效果/含义
"""

SYS: str = sys.platform


def abs_cwd_base(path):
    """
    获取当前【进程工作目录】为基准开始的某个路径的绝对路径
    """
    pwd = os.getcwd()
    return os.path.join(pwd, path)


def abs_cwd():
    """进程工作目录"""
    return os.getcwd()


def abs_file():
    """
    获取调用此函数的文件的绝对路径
    :return:
    """
    return traceback.extract_stack()[-2].filename


def abs_file_base(file, path=''):
    """
    获取当前【调用此函数的文件的上级目录】为基准开始的某个路径的绝对路径
    :param file :请传入 __file__
    :param path: 上级目录下的文件路径位置
    :return:
    """
    db_path = os.path.dirname(os.path.abspath(file))
    return os.path.join(db_path, path)


def abs_find_file(path, suffix):
    """
    寻找某个绝对路径下的某个文件，返回
    :param path: 基准路径
    :param suffix: 文件名
    :return: 文件绝对路径
    """
    try:
        res = [os.path.join(root, file) for root, dirs, files in os.walk(path) for file in files if
               file.endswith(suffix)]
        if res and len(res) == 1:
            return res[0]
        else:
            return False
    except Exception:
        return False


def abs_find_program(program):
    """
    Protected method enabling the object to find the full path of a binary
    from its PATH environment variable.
    :param program: name of a binary for which the full path needs to
    be discovered.
    :return: the full path to the binary.
    :todo: add a default path list in case PATH is empty.
    """
    __is_windows = (SYS == 'win32')
    split_char = ';' if __is_windows else ':'
    program = program + '.exe' if __is_windows else program
    paths = os.environ.get('PATH', '').split(split_char)
    for path in paths:
        if (os.path.exists(os.path.join(path, program)) and not
        os.path.isdir(os.path.join(path, program))):
            if not __is_windows:
                return os.path.join(path, program)
            else:
                return '\"' + os.path.join(path, program) + '\"'
    return None


def abs_find_real_link(bath_path: str):
    """
    传入文件的绝对路径，返回文件的源文件的绝对路径
    :param bath_path:
    :return:
    """
    if os.path.islink(bath_path):
        real_link = os.readlink(bath_path)
        bath_path = os.path.abspath(os.path.dirname(bath_path))
        path = os.path.join(bath_path, real_link)
        return abs_find_real_link(path)
    else:
        return bath_path


def abs_folder_files(folder):
    result = []
    folder = path(folder)
    assert folder.is_dir()
    for file in folder.iterdir():
        result.append(str(file))
    return result


def safe_path(p):
    return p.replace('/', '\\') if SYS == 'win32' else p.replace('\\', '/')


def path(p):
    return Path(p)


def _combine_path(path_a, path_b):
    pass


def gain_path_files(_path):
    files = list(list(os.walk(_path))[0])[2]

    return files
