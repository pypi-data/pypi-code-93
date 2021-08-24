# -*- coding: utf-8 -*-
__author__ = 'renato'


import jsonpickle
from li_common.helpers import to_camel_case

def serialize(cls, data_type=True):
    if data_type:
        return jsonpickle.encode(cls)
    else:
        json_str = jsonpickle.encode(cls, unpicklable=False)
        json_resp = jsonpickle.decode(json_str)
        data = None
        if type(json_resp) is dict:
            data = loop_dic(json_resp)
        elif type(json_resp) is list:
            data = loop_list(json_resp)

        return jsonpickle.encode(data, unpicklable=False)


def descerialize(values, cls=None):
    obj = jsonpickle.decode(values)
    result = None

    if cls is not None and type(obj) is dict:
        result = cls.from_dic(obj)
    else:
        result = obj

    return result

def loop_dic(values):
    data = {}
    for key, value in values.items():
        # print key, value
        if type(value) is dict:
            data[to_camel_case(key)] = loop_dic(value)
        elif type(value) is list:
            data[to_camel_case(key)] = loop_list(value)
        else:
            data[to_camel_case(key)] = value

    return data


def loop_list(values):
    data = []
    for value in values:
        if type(value) is dict:
            data.append(loop_dic(value))
        elif type(value) is list:
            data.append(loop_list(value))
        else:
            data.append(value)

    return data