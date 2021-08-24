"""
util.py 工具包
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/25/21 5:13 PM
"""

import os
import re
from importlib import import_module


def load_object(path: str):
    """
    Load an object given its absolute object path, and return it.
    object can be a class, function, variable or an instance.
    path ie: 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware'
    """

    dot = path.rindex('.')
    module, name = path[:dot], path[dot + 1:]
    mod = import_module(module)
    return getattr(mod, name)


def is_valid_name(name: str):
    if (not name) or (not isinstance(name, str)) or name.endswith('.'):
        return False
    if re.findall(r'[/\\*?\"\'<>|;]|\.\.', name):
        return False
    return True


def is_allowed_extension(file_name: str, allowed_extensions: list = None, denied_extensions: list = None):
    """
    判断是否为允许的扩展名
    :param file_name: 文件名
    :param allowed_extensions: 允许的扩展名
    :param denied_extensions: 禁止的扩展名
    :return:
    """

    if denied_extensions is None:
        denied_extensions = []
    if allowed_extensions is None:
        allowed_extensions = []

    allowed_extensions = ['.' + i.lower() for i in allowed_extensions]
    denied_extensions = ['.' + i.lower() for i in denied_extensions]
    _file_name, _file_extension = os.path.splitext(file_name)
    file_extension = _file_extension.lower()

    if not file_extension:
        return False

    if denied_extensions and (file_extension in denied_extensions):
        return False

    if allowed_extensions and (file_extension not in allowed_extensions):
        return False

    return True


def is_allowed_regex(string: str, regex_list: list = None) -> bool:
    """
    检查 sting 是否在 regex_list 允许范围内（正则匹配）
    :param string:
    :param regex_list:
    :return:
    """
    if not string:
        return False

    if not regex_list:
        return True

    regex_string = '|'.join(regex_list)
    regex = '^({regex_string})$'.format(regex_string=regex_string)
    regex_compile = re.compile(regex, re.I | re.U)
    return not bool(re.match(regex_compile, string))


def build_url(*args, left_index=None, right_index=None):
    """
    url 拼装
    :param args:
    :param left_index:
    :param right_index:
    :return:
    """

    if len(args) and args[0].replace('\\', '/') == '/':
        return '/'

    if left_index is None:
        left_index = args[0].startswith('/')

    if right_index is None:
        right_index = args[-1].endswith('/')

    urls = []

    for arg in args:
        if not isinstance(arg, str):
            continue
        arg = arg.replace('\\', '/')
        if arg == '/':
            continue
        if arg.endswith('//') and arg.startswith('//'):
            arg = arg[1:-1]
        elif arg.endswith('//') and not arg.startswith('//'):
            arg = arg[0:-1].lstrip('/')
        elif not arg.endswith('//') and arg.startswith('//'):
            arg = arg[1:].rstrip('/')
        else:
            arg = arg.strip('/')
        urls.append(arg)

    url = '/'.join(urls)

    if url.startswith('https://') or url.startswith('http://') or url.startswith('//'):
        left_index = False

    if url.endswith('/'):
        right_index = False

    if left_index:
        url = '/' + url
    if right_index:
        url = url + '/'
    return url


def hump2underline(hump_str):
    p = re.compile(r'([a-z]|\d)([A-Z])')
    sub = re.sub(p, r'\1_\2', hump_str).lower()
    return sub


def underline2hump(underline_str):
    sub = re.sub(r'(_\w)', lambda x: x.group(1)[1].upper(), underline_str)
    return sub


class Dict(dict):
    """
    自定义字典类，解决多级取值，赋值问题
    """

    def __missing__(self, key):
        value = self[key] = type(self)()
        return value
