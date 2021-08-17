# -*- coding: utf-8 -*-

import json
import time
import random
import re
import datetime
import os
import string
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from x_py_libs.libs import JSONObject


class UtilitiesHelper(object):
    def __init__(self):
        pass

    """[summary]
        json -> str
    Returns:
        [type] -- [description]
    """
    @staticmethod
    def json_dumps(data, ensure_ascii=True):
        return json.dumps(data, ensure_ascii=ensure_ascii)

    """[summary]
        json -> str
    Returns:
        [type] -- [description]
    """
    @staticmethod
    def json_dumps_dict(data, ensure_ascii=True):
        return json.dumps(data, default=lambda obj: UtilitiesHelper.json_default(obj), ensure_ascii=ensure_ascii)

    @staticmethod
    def json_default(value):
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        else:
            return value.__dict__

    """[summary]
        str -> json
    Returns:
        [type] -- [description]
    """
    @staticmethod
    def json_loads_object_hook(data):
        return json.loads(data, object_hook=JSONObject)

    """[summary]
        str -> json
    Returns:
        [type] -- [description]
    """
    @staticmethod
    def json_loads(data):
        return json.loads(data)

    @staticmethod
    def decode_unicode(data):
        return data.replace('\n', '\\n').encode('utf-8').decode('unicode-escape')
        # return data.replace('\\"', '\\\\"').encode('utf-8').decode('unicode-escape').replace('\n', '\\n')
        # return data

    @staticmethod
    def tuple_to_dict(data, key_list):
        return dict(map(lambda x, y: (x, y), key_list, data))

    """[summary]

    Returns:
        yyyymmdd
    """
    @staticmethod
    def now_date():
        return UtilitiesHelper.now(f='%Y%m%d')

    """[summary]

    Returns:
        yyyy-mm-dd
    """
    @staticmethod
    def today():
        return datetime.date.today()

    """[summary]

    Returns:
        yyyy-mm-dd
    """
    @staticmethod
    def today_str():
        return str(UtilitiesHelper.today())

    @staticmethod
    def now_time():
        return UtilitiesHelper.now(f='%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_timestamp():
        return UtilitiesHelper.now('%Y%m%d%H%M%S')

    @staticmethod
    def now(f=None):
        if f is None:
            return time
        return time.strftime(f)

    @staticmethod
    def get_obj_property_names(obj):
        property_names = [p for p in dir(obj) if isinstance(getattr(obj, p), property)]
        return property_names

    @staticmethod
    def get_cls_fields_values(cls):
        fields = []
        values = []
        for prop in cls.__dict__:
            fields.append(prop)
            values.append(getattr(cls, prop))

        return fields, values

    @staticmethod
    def get_proj_root_path(root_path_name='backend'):
        current_path = os.path.abspath(os.path.dirname(__file__))
        root_path = current_path[:current_path.find(root_path_name)+len(root_path_name)]
        return root_path

    @staticmethod
    def sleep(t):
        time.sleep(t)

    @staticmethod
    def random(start=1000, stop=9999):
        return random.randrange(start, stop)

    @staticmethod
    def sub_non_numeric(text, numeric=True):
        number = re.sub('[^0-9]', '', text)
        if numeric:
            if number is not None and number != '':
                return int(number)
            return 0
        return number

    @staticmethod
    def filter_char(pattern, repl, text):
        if text is None:
            return ''
        return re.sub(pattern, repl, text)

    @staticmethod
    def check_url(path, prefix):
        return ('' if len(re.findall('http[s]?:\/\/', path)) > 0 else prefix) + path

    @staticmethod
    def get_char_list():
        # 1
        a = list(map(chr, range(ord('a'), ord('z') + 1)))
        # 2
        b = [chr(x) for x in range(ord('a'), ord('z') + 1)]
        # 3
        letter_list = string.ascii_letters
        number_list = string.digits
        numbers_letters = string.ascii_letters + string.digits

        return a

    @staticmethod
    def get_longest(arr, key=None):
        max_length, longest_element = max([(len((x if key is None else x.get(key))), x) for x in arr])
        return max_length, longest_element

    @staticmethod
    def get_length(char):
        try:
            row_l = len(char)
            utf8_l = len(char.encode('utf-8'))
            # print(char, row_l, utf8_l)
            return int((utf8_l - row_l) / 2 + row_l)
        except:
            return None
        return None

    @staticmethod
    def remove_list_empty(_list):
        while '' in _list:
            _list.remove('')
        return _list

    @staticmethod
    def camel_2_snake(value):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def serializer(value, **kwargs):
        return Serializer(value, **kwargs)
