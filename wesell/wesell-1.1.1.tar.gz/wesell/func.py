# -*- coding: utf-8 -*-
import sys
import pkgutil
import importlib
import inspect
from datetime import datetime


def pycallable(func):
    if sys.version_info.major == 2:
        return callable(func)
    else:
        return hasattr(func, '__call__')

def compact(*names):
    """
    打包变量为字典
    :param names:
    :return:
    """
    caller = inspect.stack()[1][0]  # caller of compact()
    vars = {}
    for n in names:
        if n in caller.f_locals:
            vars[n] = caller.f_locals[n]
        elif n in caller.f_globals:
            vars[n] = caller.f_globals[n]
    return vars


def extract(vars):
    """
    提取字典为变量
    :param vars:
    :return:
    """
    caller = inspect.stack()[1][0]  # caller of extract()
    for n, v in vars.items():
        caller.f_locals[n] = v  # NEVER DO THIS - not guaranteed to work


# 可转化字符串类型的数字为int
def isint_or(var, replace=0):
    """
    判断是否int, 否则使用replace替换
    :param var:
    :param replace:
    :return:
    """
    if sys.version_info.major == 2:
        # python2
        if isinstance(var, int) or isinstance(var, long):
            return var
        if isinstance(var, (str, unicode)) and var.isdigit():
            return int(var)
        return replace
    else:
        # python3
        if isinstance(var, int):
            return var
        if isinstance(var, str) and var.isdigit():
            return int(var)
        return replace


# 拼接数据为字符串
# 当把一组ID用逗号分割拼接为字符串时, 使用 str.join()会报错
# 故需要一个拼接方法, 自适应数据类型拼接成字符串
def implode(sep, items):
    """
    拼接数据为字符串
    :param sep: 间隔字符
    :param items: 数据元组
    :return: string, 拼接后的字符串

    nums = [1,2,3,4,5]
    nums = implode(":", nums) // >> "1:2:3:4:5"

    """
    return str(sep).join(map(__stringify, items))


def splitids(str):
    """
    分离id串为int数组
    :para str: id串
    :return:   list(ids)
    """
    str = str.strip()
    if not str:
        return []
    return list(map(lambda id: int(id), str.split(",")))


def __stringify(v):
    """
    implode 转化数据为字符串回调方法
    """
    if v is None:
        return ''
    if sys.version_info.major == 2:
        # python2
        if isinstance(v, (str, unicode)) and len(v) == 0:
            return ''
        if isinstance(v, (str, unicode)):
            return v
        return "%s" % (v,)
    else:
        # python3
        if isinstance(v, str) and len(v) == 0:
            return ''
        if isinstance(v, str):
            return v
        return "%s" % (v,)


def import_submodules(package_name):
    """ Import all submodules of a module, recursively

    :param package_name: Package name
    :type package_name: str
    :rtype: dict[types.ModuleType]
    """
    package = sys.modules[package_name]
    return {
        name: importlib.import_module(package_name + '.' + name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__)
        }


def list_or_args(keys, args):
    # returns a single list combining keys and args
    try:
        iter(keys)
        # a string or bytes instance can be iterated, but indicates
        # keys wasn't passed as a list
        if isinstance(keys, (str, bytes)):
            keys = [keys]
        if len(args):
            keys = [keys]
    except TypeError:
        keys = [keys]
    if args:
        keys.extend(args)
    return keys


def strftime(time=None):
    # 返回SQL时间串
    if not time:
        time = datetime.now()
    return time.strftime("%Y-%m-%d %H:%M:%S")


def strptime(timestr):
    return datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")


def isstr(val):
    if sys.version_info.major == 2:
        return isinstance(val, (str, unicode))
    else:
        return isinstance(val, str)
