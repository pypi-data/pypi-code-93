# coding: utf-8
import json
from datetime import date, datetime, timedelta
from typing import Union, Tuple

import dateutil.parser
from dateutil import tz

__all__ = [
    "get_default_session",
    "set_default_session",
    "close_session",
    "set_app_key",
    "set_log_level",
]


def is_string_type(value):
    try:
        return isinstance(value, basestring)
    except NameError:
        return isinstance(value, str)


def get_json_value(json_data, name):
    if name in json_data:
        return json_data[name]
    else:
        return None


def to_datetime(
    date_value: Union[str, timedelta, Tuple[datetime, date]]
) -> Union[tuple, datetime, None]:
    if date_value is None:
        return None

    if isinstance(date_value, timedelta):
        return datetime.now(tz.tzlocal()) + date_value

    if isinstance(date_value, (datetime, date)):
        return date_value

    try:
        return dateutil.parser.parse(date_value)
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(e)


def _to_utc(datetime_value):
    if datetime_value is None:
        return None
    _value = to_datetime(datetime_value)
    UTC = tz.gettz("UTC")
    _value = _value.astimezone(UTC).replace(tzinfo=None)
    return _value


def to_utc_datetime(datetime_value):
    datetime_value = _to_utc(datetime_value)
    if datetime_value is None:
        return None
    return datetime_value  # .strftime("%Y-%m-%d %H:%M:%S")


def to_utc_date(date_value):
    date_value = _to_utc(date_value)
    if date_value is None:
        return None
    return date_value.date()


def to_utc_datetime_isofmt(datetime_value):
    datetime_value = _to_utc(datetime_value)
    if datetime_value is None:
        return None
    datetime_value = datetime_value.isoformat(timespec="microseconds") + "000Z"
    return datetime_value


def get_date_from_today(days_count):
    if type(days_count) != int:
        raise ValueError(
            "The parameter {} should be an integer, found {}".format(
                days_count, type(days_count)
            )
        )
    return datetime.now(tz.tzlocal()) + timedelta(days=-days_count)


def is_list_of_string(values):
    return all(is_string_type(value) for value in values)


def check_for_string(parameter, name):
    if not is_string_type(parameter):
        raise ValueError(
            "The parameter {} should be a string, found {}".format(name, str(parameter))
        )


def check_for_string_or_list_of_strings(parameter, name):
    if type(parameter) != list and (not parameter or not is_string_type(parameter)):
        raise ValueError(
            "The parameter {} should be a string or a list of string, found {}".format(
                name, type(parameter)
            )
        )
    if type(parameter) == list and not is_list_of_string(parameter):
        raise ValueError(
            "All items in the parameter {} should be of data type string, found {}".format(
                name, [type(v) for v in parameter]
            )
        )


def check_for_int(parameter, name):
    if type(parameter) is not int:
        raise ValueError(
            "The parameter {} should be an int, found {} type value ({})".format(
                name, type(parameter), str(parameter)
            )
        )


def build_list_with_params(values, name):
    if values is None:
        raise ValueError(name + " is None, it must be a string or a list of strings")

    if is_string_type(values):
        return [(v, None) for v in values.split()]
    elif type(values) is list:
        try:
            return [
                (value, None) if is_string_type(value) else (value[0], value[1])
                for value in values
            ]
        except Exception:
            raise ValueError(
                name
                + " must be a string or a list of strings or a tuple or a list of tuple"
            )
    else:
        try:
            return values[0], values[1]
        except Exception:
            raise ValueError(
                name
                + " must be a string or a list of strings or a tuple or a list of tuple"
            )


def build_list(values, name):
    if values is None:
        raise ValueError(name + " is None, it must be a string or a list of strings")

    if is_string_type(values):
        return [values.strip()]
    elif type(values) is list:
        if all(is_string_type(value) for value in values):
            return [value for value in values]
        else:
            raise ValueError(name + " must be a string or a list of strings")
    else:
        raise ValueError(name + " must be a string or a list of strings")


def build_dictionary(dic, name):
    if dic is None:
        raise ValueError(
            name + " is None, it must be a string or a dictionary of strings"
        )

    if is_string_type(dic):
        return json.loads(dic)
    elif type(dic) is dict:
        return dic
    else:
        raise ValueError(name + " must be a string or a dictionary")


def tz_replacer(s):
    if isinstance(s, str):
        if s.endswith("Z"):
            s = s[:-1]
        elif s.endswith("-0000"):
            s = s[:-5]
        if s.endswith(".000"):
            s = s[:-4]
    return s


def set_default_session(session):
    DefaultSession.set_default_session(session)


def get_default_session(app_key=None):
    return DefaultSession.get_default_session(app_key)


def close_session():
    DefaultSession.get_default_session().close()


def set_app_key(app_key):
    from refinitiv.dataplatform.core.session.session import Session

    _session = get_default_session(app_key)
    if _session.get_open_state() == Session.State.Closed:
        _session.open()


def set_log_level(log_level):
    from refinitiv.dataplatform.core.session.session import Session

    default_session = DefaultSession.get_default_session()
    default_session.set_log_level(log_level)


class DefaultSession(object):
    # singleton session
    __default_session = None

    @classmethod
    def set_default_session(cls, session):
        from refinitiv.dataplatform.core.session.session import Session

        if isinstance(session, Session):
            cls.__default_session = session

    @classmethod
    def get_default_session(cls, app_key=None):
        from refinitiv.dataplatform.core.session.desktop_session import DesktopSession

        if cls.__default_session is None:
            if app_key is None:
                return None
            cls.__default_session = DesktopSession(app_key)
        elif app_key is not None:
            if app_key != cls.__default_session.app_key:
                cls.__default_session.close()
                cls.__default_session = DesktopSession(app_key)

        return cls.__default_session

    @classmethod
    def close_default_session(cls):
        if cls.__default_session is not None:
            cls.__default_session.close()
