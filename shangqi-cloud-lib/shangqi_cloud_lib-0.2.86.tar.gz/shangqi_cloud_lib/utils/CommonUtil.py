import datetime
import inspect
import json
import logging
import random
import re
import socket
import time
import sys
from decimal import Decimal
from functools import reduce

from bson import ObjectId


def generate_random_key(code_len=6):
    all_char = '0123456789qazwsxedcrfvtgbyhnujmikolpQAZWSXEDCRFVTGBYHNUJIKOLP'
    index = len(all_char) - 1
    code = ''
    for _ in range(code_len):
        num = random.randint(0, index)
        code += all_char[num]
    return code


def pascal_case_to_snake_case(camel_case: str):
    """大驼峰（帕斯卡）转蛇形"""
    snake_case = re.sub(r"(?P<key>[A-Z])", r"_\g<key>", camel_case)
    return snake_case.lower().strip('_')


def snake_case_to_pascal_case(snake_case: str):
    """蛇形转大驼峰（帕斯卡）"""
    words = snake_case.split('_')
    return ''.join(word.title() for word in words)


def sys_date_format(dt=datetime.datetime.now(), format="%Y-%m-%d %H:%M:%S", type="datetime", delta=0):
    if delta == 0:
        sys_date = dt.strftime(format)
    else:
        sys_date = (dt - datetime.timedelta(delta)).strftime(format)
    if type == "datetime":
        return sys_date
    elif type == "date":
        return sys_date.split(" ")[0]
    elif type == "time":
        return sys_date.split(" ")[-1]


def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def split_comma_str(item):
    if not item or len(item.strip()) == 0:
        return []
    else:
        return str(item).split(",")


def split_comma_int(item):
    res = []
    if not item or len(item.strip()) == 0:
        return res
    for v in item.split(","):
        if "-" in v:
            [start, stop] = v.split("-")
            for i in range(int(start), int(stop) + 1):
                res.append(i)
        elif ":" in v:
            [start, step, stop] = v.split(":")
            if len(step) == 0:
                step = '1'
            for i in range(int(start), int(stop) + 1, int(step)):
                res.append(i)
        else:
            res.append(int(v))
    return res


def is_not_empty(obj):
    if not obj or len(str(obj).strip()) == 0:
        return False
    return True


def is_empty(obj):
    if not obj or len(str(obj).strip()) == 0:
        return True
    return False


def check_empty(**kwargs):
    for key, val in kwargs.items():
        if is_empty(val):
            raise Exception("缺少必要的参数: {}".format(key))


def validate_date(date):
    try:
        date_str = str(date)
        if ":" in date_str:
            if len(date_str) < 19:
                time.strptime(date_str, "%Y-%m-%d %H:%M")
            else:
                time.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        else:
            time.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


# 用于判断一个字符串是否符合Json格式
def check_json_format(raw_msg):
    if isinstance(raw_msg, str):  # 首先判断变量是否为字符串
        try:
            json.loads(raw_msg, encoding='utf-8')
        except ValueError:
            return False
        return True
    else:
        return False


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.timedelta):
            return str(obj)
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, tuple):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)


# 获取方法参数默认值
def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


# 获取方法参数类型
def get_annotation_args(func):
    signature = inspect.signature(func)
    return {
        k: v.annotation
        for k, v in signature.parameters.items()
    }


def get_func_params(func):
    func_params = func.__code__.co_varnames
    if func_params and len(func_params) > 1:
        return func_params[1:func.__code__.co_argcount]
    else:
        logging.warning(f"方法：{func.__name__}未获取到参数！")
        return []


# 解析param
def parse_val(val, val_type):
    new_val = val
    if isinstance(val, bytes) or isinstance(val, bytearray):
        new_val = val.decode("utf-8")
    if isinstance(val, list):
        val_list = []
        for item in val:
            val_item = parse_val(item, None)
            val_list.append(val_item)
        if val_type == list:
            return val_list
        else:
            new_val = val_list
    if type(new_val) != val_type:
        if val_type == int:
            return int(new_val)
        elif val_type == str and isinstance(new_val, list):
            return new_val[0]
        else:
            return new_val
    return new_val


# 解析command
def get_command(self, func_name):
    command = ""
    params = None
    is_json = False
    if "get" in func_name:
        command = self.get_argument("command", "")
    elif "post" in func_name:
        params_str = ""
        if not self.request.files and len(self.request.body.decode('utf8')) > 0:
            params_str = self.request.body.decode('utf8')
            is_json = check_json_format(params_str)
        if is_json:
            params = json.loads(params_str)
            command = params.get("command", "")
        else:
            params = self.request.arguments
            command = self.get_argument("command", "")
            command = parse_val(command, str)
        if self.request.files:
            files_dict = self.request.files
            for key in files_dict:
                params[key] = files_dict[key]
    return command, params, is_json


# 进度条打印
def print_process(index, count, start_time, desc=""):
    percent = round((index + 1) / count * 100, 2)
    process = int(percent)
    process_str = '>' * process + '-' * (100 - process)
    item_time = datetime.datetime.now()
    remain_time = (item_time - start_time) / (index + 1) * (count - index - 1)
    sys.stdout.write('\r' + process_str + '[%s%%]' % percent + f'{desc}:({index + 1}/{count})  预计剩余时间：{remain_time}')
    sys.stdout.flush()
    if index == count - 1:
        end_time = datetime.datetime.now()
        print(f"\r{desc}执行完成！用时：{end_time - start_time}")


# 去空
def eliminate_empty(list):
    return [x for x in list if x is not None]


def list_dict_duplicate_removal(data_list):
    run_function = lambda x, y: x if y in x else x + [y]
    return reduce(run_function, [[], ] + data_list)


def format_dict_key(data_dict, key_scope_start: int = 0, key_scope_end: int = 2147483647):
    new_data = {}
    for d in data_dict:
        new_data[d[key_scope_start:key_scope_end]] = data_dict[d]
    return new_data


def database_sql_paging(page_size, page_number):
    limit_number = int(page_size)
    skip_number = (int(page_number) - 1) * int(page_size)

    return limit_number, skip_number

#字典列表 转以key为键的字典
def dict_in_list_to_dict(key, data_list):
    data_dict = {}
    for data in data_list:
        if data[key] in data_dict.keys():
            list_value = data_dict[data[key]]
            list_value.append(data)
        else:
            list_value = [data]
            data_dict[data[key]] = list_value
    return data_dict
