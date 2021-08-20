# coding: utf8


def _convert_to_str(from_type, values, some):
    result = None

    if isinstance(some, str):
        result = from_type.normalize(some)
    elif isinstance(some, from_type):
        result = some.value

    if result:
        return result
    else:
        raise TypeError(f"{from_type.__name__} value must be in {values}")


def _normalize(lower_values, some):
    some_lower = some.lower()
    enum_some = lower_values.get(some_lower)
    result = ""

    if enum_some:
        result = enum_some.value
    return result


def is_enum_equal(enum_value, some):
    c = enum_value.__class__
    try:
        s = c.convert_to_str(some)
        is_equal = enum_value.value == s
    except TypeError:
        is_equal = False
    return is_equal
