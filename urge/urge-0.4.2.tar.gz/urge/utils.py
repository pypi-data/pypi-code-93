import typing as t


class NoobError(Exception):
    '''Everybody Makes a Mistake'''

    pass


class TimeUnitError(NoobError):
    '''Typo Invalid and Empty'''

    pass


class DumbEmptyError(NoobError):
    pass


class CarelessFunctionError(NoobError):
    '''Ugh'''

    pass


class InvalidUrlError(NoobError):
    pass


def convert_time(time: t.Dict[int, str]) -> int:
    if not time:
        raise DumbEmptyError(
            'Put time value and unit in KV(dict) pairs , or just use seconds'
        )

    val, unit = list(time.items())[0]

    if unit == 'seconds':
        return val
    elif unit == 'minutes':
        return round(val / 60)
    elif unit == 'hours':
        return round(val / 360)
    else:
        raise TimeUnitError(
            f'{unit} is not a valid time unit, try to use "seconds minutes or hour..."'
        )


def callable_check(func: t.Callable):
    if not isinstance(func, t.Callable):
        raise CarelessFunctionError(f'{func} must be a function')


def drop(d: t.Dict, keys: t.List[str]):
    for k in keys:
        if k not in d.keys():
            # Test if there really exists the key need to be droped
            # if not, act like normal loop, and pretending nothing happend
            continue
        d.pop(k)
    return d
