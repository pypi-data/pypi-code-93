from typing import *

import base64
import calendar
import json
from datetime import date, datetime


JSONEncoder = json.JSONEncoder
JSONDecoder = json.JSONDecoder
JSONDecodeError = json.JSONDecodeError


_DEFAULT_SMART_DATE_SUFFIX = '_str'


def _process_obj(obj: Any, smart_date: bool = True, smart_date_suffix: str = None):
    smart_date_suffix = smart_date_suffix if isinstance(smart_date_suffix, str) else _DEFAULT_SMART_DATE_SUFFIX

    if obj is None or isinstance(obj, (str, int, float, bool)):
        ret = obj
    elif isinstance(obj, bytes):
        try:
            ret = obj.decode('utf-8')
        except UnicodeDecodeError:
            ret = 'data:{}'.format(base64.b64encode(obj).decode('utf-8'))
    elif isinstance(obj, (list, tuple, set)):
        ret = list()
        for i in range(len(obj)):
            ret.append(_process_obj(obj[i], smart_date, smart_date_suffix))
    elif isinstance(obj, dict):
        ret = dict()
        for k, v in obj.items():
            k = str(k)
            ret[k] = _process_obj(v, smart_date, smart_date_suffix)
            if smart_date:
                if isinstance(v, datetime):
                    ret[f'{k}{smart_date_suffix}'] = v.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(v, date):
                    ret[f'{k}{smart_date_suffix}'] = v.strftime('%Y-%m-%d')
    elif isinstance(obj, date):
        ret = calendar.timegm(obj.timetuple())
    else:
        ret = str(obj)

    return ret


def load(
    fp,
    *,
    cls: Optional[Type[JSONDecoder]] = None,
    object_hook: Optional[dict] = None,
    parse_float: Optional[Callable] = None,
    parse_int: Optional[Callable] = None,
    parse_constant: Optional[Callable] = None,
    object_pairs_hook: Optional[Callable] = None,
    **kw
):
    return json.load(
        fp=fp,
        cls=cls,
        object_hook=object_hook,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        object_pairs_hook=object_pairs_hook,
        **kw
    )


def dump(
    obj,
    fp,
    *,
    skipkeys: bool = False,
    ensure_ascii: bool = True,
    check_circular: bool = True,
    allow_nan: bool = True,
    cls: Optional[Type[JSONEncoder]] = None,
    indent: Union[None, int, str] = None,
    separators: Optional[Tuple[str, str]] = None,
    default: Optional[Callable] = None,
    sort_keys: bool = False,
    smart_date: bool = True,
    smart_date_suffix: str = None,
    **kw
):
    return json.dump(
        _process_obj(obj, smart_date, smart_date_suffix),
        fp=fp,
        skipkeys=skipkeys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        cls=cls,
        indent=indent,
        separators=separators,
        default=default,
        sort_keys=sort_keys,
        **kw
    )


def loads(
    s: Union[str, bytes],
    cls: Optional[Type[JSONDecoder]] = None,
    object_hook: Optional[dict] = None,
    parse_float: Optional[Callable] = None,
    parse_int: Optional[Callable] = None,
    parse_constant: Optional[Callable] = None,
    object_pairs_hook: Optional[Callable] = None,
    **kw
):
    return json.loads(
        s,
        cls=cls,
        object_hook=object_hook,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        object_pairs_hook=object_pairs_hook,
        **kw
    )


def dumps(
    obj: Any,
    skipkeys: bool = False,
    ensure_ascii: bool = True,
    check_circular: bool = True,
    allow_nan: bool = True,
    cls: Optional[Type[JSONEncoder]] = None,
    indent: Union[None, int, str] = None,
    separators: Optional[Tuple[str, str]] = None,
    default: Optional[Callable] = None,
    sort_keys: bool = False,
    smart_date: bool = True,
    smart_date_suffix: str = None,
    **kw
):
    return json.dumps(
        _process_obj(obj, smart_date, smart_date_suffix),
        skipkeys=skipkeys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        cls=cls,
        indent=indent,
        separators=separators,
        default=default,
        sort_keys=sort_keys,
        **kw)
