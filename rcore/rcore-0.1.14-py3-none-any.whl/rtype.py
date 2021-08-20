from __future__ import annotations

import typing as _T
from typing import get_type_hints
import unittest

class Validator(object):
    """ Интерфес для проверки случайных данных от пользователя.

    Например в rcore.config и rcore.cliengine

    """

    types: list[type]
    enum: list[_T.Any]
    default: _T.Any

    def __init__(self, types: _T.Union[type, list[type], None] = None, enum: _T.Union[list[_T.Any], None] = None, default: _T.Any = Exception):
        """ Инициализация объекта

        Args:
            types (type, list[type]): Тип / список типов, к которым должно относиться проверяемое значение.
            enum (list[str]): Множество значений в которое должно входить проверяемое значение. Defaults to empty list.
                Если множество пустое, то проверка проводиться не будет.
            default (t.Any, optional): Значение по умолчанию, если входное на проверку значение равно None. Defaults to Exception.
                Если значение по умолчанию не указано и входное значение равно None, проверка выдаст исключение.

        """

        if types is None:
            self.types = list()
        else:
            self.types = types if isinstance(types, list) else [types]

        if enum is None:
            self.enum = list()
        else:
            self.enum = enum

        self.default = default

    def check(self, value: _T.Any, swapType: bool = False):
        """ Проверка значения на соблюдения типов

        Args:
            value (_T.Any): Проверяемое значение
            swapType (bool): Пытаться привести значение к типам

        """

        if value is None:
            if self.default is Exception:
                raise ValueError('No value - No default - Yes Exception')
            else:
                value = self.default
        elif len(self.types) > 0 or len(self.enum) > 0:
            passed = False

            if len(self.types) > 0:
                for type_ in self.types:
                    passed = type(value) == type_
                    if passed:
                        break
                    elif swapType:
                        try:
                            newValue = swap_type(value, type_)
                        except TypeError:
                            pass
                        else:
                            value = newValue
                            passed = True
                            break

            if len(self.enum) > 0:
                for enumItem in self.enum:
                    if enumItem == value:
                        passed = True
                        break
                    elif swapType:
                        try:
                            newValue = swap_type(value, type(enumItem))
                        except TypeError:
                            pass
                        else:
                            if newValue == enumItem:
                                value = newValue
                                passed = True
                                break

            if not passed:
                raise TypeError(f'The value "{value}" was not validated')

        return value


def check(value: _T.Any, hint: type):
    """ Проверка значения value на соблюдение типа hint

    Args:
        value (_T.Any): Значение для проверки
        hint (type): Инструкция типов

    """

    valueType = type(value)

    isError = True

    if isinstance(hint, list):
        for type_ in hint:
            if type_ == valueType:
                isError = False
                break

    elif hint == valueType:
        isError = False

    if isError:
        raise TypeError(f'the value "{value}" does not match the type mask "{hint}"')


def print_error(parameter: str, value: _T.Any, types: list[type]):
    raise TypeError(
        f'The value "{value}" is not suitable for the "{parameter}" parameter, one of the values ​​from this list is required "{types}"'
    )


def checker(parameter: str, value: _T.Any, types: list[type]):
    if not isinstance(value, tuple(types)):
        print_error(parameter, value, types)


def optional(parameter: str, value: _T.Any, types: list[type]):
    if value is not None:
        checker(parameter, value, types)


def _strict_check(param: str, hint: type, getValue: _T.Any):

    try:
        check(getValue, hint)

    except TypeError:
        raise TypeError(f'Type of {param} is {type(getValue)} and not {hint}')


def _strict(function: _T.Callable, hints: _T.Union[dict, None] = None, args: tuple = tuple(), kwargs: dict = {}, result: _T.Any = None):

    if hints is None:
        hints = get_type_hints(function)

    all_args = kwargs.copy()
    all_args.update(dict(zip(function.__code__.co_varnames, args)))

    for param in all_args:
        if param == 'self':
            continue

        try:
            _strict_check(param, hints[param], all_args[param])
        except KeyError:
            raise TypeError(f'The formal parameter "{param}" was not given a type')

    try:
        _strict_check('return', hints['return'], result)
    except KeyError:
        raise TypeError('The return formal parameter was not given a type')


def strict(function):
    """ Декоратор проверяющий соблюдение типов """

    hints = get_type_hints(function)

    def type_checker(*args, **kwargs):
        result = function(*args, **kwargs)
        _strict(function, hints, args, kwargs, result)
        return result

    return type_checker


class newstrict(object):
    pass


def swap_type(value: _T.Any, type_: type) -> _T.Any:
    """ Преобразование значения в другой тип.

    Args:
        value (_T.Any): Значение для преобразования
        type_ (type): Тип, в который будет преобразованно значение

    Raises:
        TypeError: Указаное значение нельзя преобразовать в указный тип.

    Returns:
        _T.Any: Значение преобразованное в другой тип

    """

    valueType = type(value)

    if valueType == type_:
        return value

    if type_ is bool:

        from . import utils

        if valueType == int:
            if value != 0:
                return True
            else:
                return False

        elif valueType == str:
            if value in utils.Str_equally_True:
                return True
            elif value in utils.Str_equally_False:
                return False

    if type_ is int:
        if isinstance(value, str):
            if value.isdigit():
                return int(value)
            else:
                try:
                    return float(value)
                except(ValueError):
                    pass

        elif isinstance(value, bool):
            if value:
                return 1
            else:
                return 0

    elif type_ is str:
        return str(value)

    raise TypeError(f'The value "{value}" cannot be converted to type "{type_}"')
