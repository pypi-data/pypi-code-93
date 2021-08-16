# -*- coding: utf-8 -*-
#
# django 模板过滤器
#


from django import template

from ..utils import json_dumps, timestamp_to_datetime_str

register = template.Library()


@register.filter(name='mydate')
def mydate(value, arg):
    if value.find('2012').size > 0:
        return value
    else:
        return value


@register.filter(name='json_dumps')
def _json_dumps(value):
    return json_dumps(value, indent=4)


@register.filter(name='multiplication')
def multiplication(value, arg):
    return value * arg


@register.filter(name='get_dict_key')
def get_dict_key(key, _dict, default=''):
    try:
        if isinstance(_dict, dict):
            return _dict.get(key, _dict.get(str(key), key))
    except Exception as e:
        return default


@register.filter(name='timestamp2datetime')
def timestamp_to_datetime(value, _f='datetime'):
    try:
        _r = timestamp_to_datetime_str(int(value), _f) if value else ''
    except Exception as e:
        _r = ''
    return _r


@register.filter(name='convertTimeJson')
def convert_times_json(value):
    ret_json = []
    for i in value:
        tmp = "%s:%s - %s:%s" % (i[0] / 3600, (i[0] % 3600) / 60, i[1] / 3600, (i[1] % 3600) / 60)
        ret_json.append(tmp)
    return " , ".join(ret_json)
