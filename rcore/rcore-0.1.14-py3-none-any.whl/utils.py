from __future__ import annotations

import datetime
import functools
import json
import os
import pathlib as pa
import re
import time
import types
import typing as _T
from copy import copy
from pprint import pprint

import rlogging

from rcore import exception as ex
from rcore import rtype
from rcore.rpath import rPath

logger = rlogging.get_logger('mainLogger')

Str_equally_True = ['True', 'true', '1', 't', 'y', 'yes']
Str_equally_False = ['False', 'false', '0', 'f', 'n', 'no']
Str_equally_None = ['None', 'none', 'Null', 'null']


class dd(object):

    def __init__(self, *args: _T.Any, s: bool = False, x: bool = True) -> None:
        super().__init__()

        logger.warning(f'Start DD function. len objects: {len(args)}')

        def __help_list(data: _T.Union[list, tuple]):
            pprint(data)

        def __help_dict(data: dict):
            pprint(data)

        if len(args) == 0:
            print('dd\n')

        for i in args:
            if isinstance(i, (list, tuple)):
                __help_list(i)
            elif isinstance(i, dict):
                __help_dict(i)
            elif isinstance(i, pa.Path):
                print(str(i))
            elif isinstance(i, object):
                if hasattr(i, '__dict__'):
                    print(type(i))
                    __help_dict(i.__dict__)
                else:
                    print(i)
            else:
                print(i)

            if s:
                print('\n\n ---------- \n\n')
            else:
                print()

        if x and not s:
            raise ex.DDExit('')

    @staticmethod
    def print_result_decorate(func: _T.Callable):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            print(result)
            return result
        return wrapper


# NO TESTS
def search_point_by_lines(filePath: rPath, point_search: int):
    """ Поиск строки на которой расположена точка

    Args:
        string (str): Строка по которой будет происходить поиск
        point_search (int): Индекс искомого символа.

    Returns:
        [type]: Индекс строки на которой расположена искомая точка

    """

    string = filePath.read()

    lines = re.split(r'\n', string)
    lens = 0
    lines_len = []
    for line in lines:
        lines_len.append(len(line))
        lens += len(line)
        if lens >= point_search:
            return lines.index(line) + 1
    return -1


def file_span_separate(filePath: rPath, spanFile: list[tuple[int, int]]) -> list[str]:
    """ 

    Raises:
        exObj: [description]
        ex.errors.DeveloperIsShitError: [description]
        ex.errors.ItemNotFound: [description]
        ValueError: [description]

    Returns:
        [type]: [description]
    """

    fileText = filePath.read()

    spans_text = list(map(
        lambda span: re.sub(r'\n', ' ', fileText[span[0]:span[1]]),
        spanFile
    ))

    return spans_text


# NO TESTS
def input_more_answer(question: list, default: int):
    """ Интерактивный вопрос у пользователя с множеством ответов.

    Args:
        question (list): Список
            [0] - Вопрос, задаваемый пользователю
            [1..N] - Ответы
        default (int): Номер ответа, который будет выбран при невалидном ответе от пользователя

    Returns:
        _T.Any: Номер ответа

    """

    logger.info('Интерактивный вопрос у пользователя с множеством ответов')

    print()
    for i in range(0, len(question)):
        if i == 0:
            print(question[i])
        else:
            print(f'  {i} :  {question[i]}')
    print()
    answer = int(input('Answer: '))
    print()

    if answer > len(question) - 1:
        answer = default

    logger.info(f'Ответ от пользователя: {answer} [{question[answer]}]')

    return answer


def input_yes_no(question: str, default: bool = False) -> bool:
    """ Интерактивный вопрос у пользователя с бинарным ответом.

    Args:
        question (str): Сообщение для пользователя
        default (bool, optional): Ответ, который будет выбран при невалидном ответе от пользователя. Defaults to False.

    Returns:
        bool: [description]

    """

    logger.info('Интерактивный вопрос у пользователя с бинарным ответом')

    print('\n', question, sep='', end='  ')

    try:
        answer = rtype.swap_type(input(), bool)

    except ex.NoChangeType:
        answer = default

    logger.info(f'Ответ от пользователя: {answer}')

    return answer


# NO TESTS
def download_file(link: str, toPath: rPath):
    """ Скачивание файла из интернета и сохранение в папку

    Args:
        link (str): Ссылка на файл.
        toPath (rPath, optional): Будущее расположение скаченного файла.

    Raises:
        requests.exceptions: Исключение от requests

    """

    logger.info('Скачивание файла по ссылке: "{link}"')

    if toPath.check():
        logger.warning(f'Скачивание приостановленно. Путь "{toPath}" занят.')
        return

    try:
        import requests

    except ImportError:
        logger.critical('Скачивание приостановленно. Не найден модуль "requests"')
        exit()

    link = link.replace('http://', '').replace('https://', '')

    try:
        response = requests.get('http://' + link)

    except Exception as exObj:
        logger.critical('Скачивание приостановленно. Исключение: "{exObj}"')
        raise exObj

    with open(str(toPath), 'wb') as file:
        file.write(response.content)
    logger.info(f'Downloaded the file from the link: "{link}"')


# NO TESTS
class rJson(object):
    """ Класс для работы с Json """

    def dump(self, attend: _T.Any) -> str:
        """ Нормализация данных для поддержки json.

        Args:
            attend (_T.Any): Данные для нормализации.

        Returns:
            str: Строка формата json.

        """

        if isinstance(attend, rDict):
            attend = attend.attend

        attend = rRecursion(attend).rDict_to_value()
        attend = rRecursion(attend).path_to_str()

        return json.dumps(attend, indent=4)

    def parse(self, string: str) -> _T.Any:
        """ Перевод строки формата json в структуры python.

        Args:
            string (str): Строка формата json.

        Returns:
            _T.Any: Объект данных

        """

        string = string.strip()

        try:
            return json.loads(string)
        except json.decoder.JSONDecodeError:
            try:
                return json.loads('{' + string + '}')
            except json.decoder.JSONDecodeError:
                return json.loads('[' + string + ']')


class rDict(object):
    """ Надстрока над словарями и списками python """

    def __copy__(self):
        return rDict(self.attend)

    def __deepcopy__(self, kwargs):
        return copy(self)

    def __eq__(self, attend):
        if isinstance(attend, rDict):
            attend = attend.attend
        return self.attend == attend

    def __str__(self):
        return str(self.attend)

    attend: dict

    def __init__(self, attend: dict = {}):
        rtype.checker('attend', attend, [dict])

        self.attend = copy(attend)

    def __rDict_norm(self, variable):
        if isinstance(variable, rDict):
            return variable.attend
        return variable

    def update(self, other: dict, merge_list: bool = False) -> rDict:
        pass

    def __add__(self, plus):
        raise ex.errors.DeveloperIsShitError('delete this pls 1')

    def merge(self, other: _T.Union[dict, rDict], merge_list: bool = False) -> rDict:
        other = other.attend if isinstance(other, rDict) else other

        def __help(varone: _T.Union[dict, list, set], vartwo: _T.Union[dict, list, set], merge_list: bool) -> dict:
            varone = varone.attend if isinstance(varone, rDict) else varone
            vartwo = vartwo.attend if isinstance(vartwo, rDict) else vartwo

            if type(varone) == type(vartwo) == dict:
                for i in vartwo:
                    varone[i] = __help(varone.get(i, None),
                                       vartwo[i], merge_list)
                return varone

            elif type(varone) == type(vartwo) == list and merge_list:
                return varone + vartwo

            elif type(varone) == type(vartwo) == set and merge_list:
                varone.update(vartwo)
                return varone

            else:
                return vartwo

        if self.attend == other and type(self.attend) in [str, int]:
            self.attend += other
        else:
            self.attend = __help(self.attend, other, merge_list)

        return self

    def get(self, keys: _T.Union[str, list[str]] = [], default: _T.Any = Exception) -> _T.Any:

        error: _T.Union[str, bool] = False
        attend = copy(self.attend)

        if not isinstance(keys, list):
            keys = [keys]

        for i in keys:
            if not error:
                if isinstance(attend, list) and isinstance(i, int):
                    if len(attend) - 1 <= i:
                        attend = attend[i]
                    else:
                        error = i

                elif isinstance(attend, dict) and isinstance(i, str):
                    if i in attend:
                        attend = attend[i]
                    else:
                        error = i

                else:
                    error = i

        if error:
            if default is Exception:
                raise ex.errors.ItemNotFound(attend, error)
            else:
                return default

        attend = self.__rDict_norm(attend)

        return attend

    def set(self, val: _T.Any, keys: _T.Union[str, list[str]], merge: bool = True):
        if isinstance(val, rDict):
            val = val.attend

        update_dict: _T.Union[_T.Any, dict] = val
        clear_dict: _T.Union[_T.Any, dict] = None

        merge_list = False

        if not isinstance(keys, list):
            keys = [keys]

        for i in keys[::-1]:
            if isinstance(i, str):
                update_dict = {i: update_dict}
                clear_dict = {i: clear_dict}
            elif isinstance(i, int):
                merge_list = True
                update_dict = [None] * i + [update_dict]
                clear_dict = [None] * i + [clear_dict]

        if not merge:
            self.merge(clear_dict, merge_list)
        self.merge(update_dict, merge_list)

    def delete(self, keys: _T.Union[str, list[str]]):

        def __help(attend: dict, keys: list):
            if len(keys) == 1:
                if keys[0] in attend:
                    del attend[keys[0]]
            else:
                if keys[0] in attend:
                    attend[keys[0]] = __help(attend[keys[0]], keys[1:])
            return attend

        if not isinstance(keys, list):
            keys = [keys]

        self.attend = __help(self.attend, keys)

    def merge_keys(self, name: str, names: list[str], mergeLists: bool = False):
        if name not in self.attend:
            self.attend[name] = {}

        newAttend = rDict(self.attend[name])
        for index in names:
            if index in self.attend:
                value = self.attend[index]
                if isinstance(value, dict):
                    newAttend.merge(value, mergeLists)
                del self.attend[index]

        self.attend[name] = newAttend.attend

    def rename_keys(self, rename):
        for oldkey in rename:
            if oldkey in self.attend:
                self.attend[rename[oldkey]] = copy(self.attend[oldkey])
                del self.attend[oldkey]


class rRecursion(object):

    attend: _T.Union[dict, list]

    def __init__(self, attend: _T.Union[dict, list]):
        self.attend = copy(attend)
        # self.attend = self.rDict_to_value()

    def core(self,
             CB: _T.Callable = lambda x, y, *args, **kwargs: x(y),
             CB_key: _T.Callable = lambda x, *args, **kwargs: x,
             CB_val: _T.Callable = lambda x, *args, **kwargs: x,
             CB_to_keys: dict[str, _T.Callable[[str], _T.Union[str, None]]] = {},
             *args, **kwargs
             ) -> dict:
        """ Шаблон для рекурсивного изменения словаря

        Args:
            CB (Callable, optional): Этот калбек принимает калбек ядра(__core_callable) и некое значение из перебираемого массива.
            CB_key (Callable, optional): Калбек для оброботки значений обрабатываемого массива.
            CB_val (Callable, optional): Калбек для оброботки ключей и пар ключей (при рекурсивной обработке словаря).
            CB_to_keys (dict, optional): Значение по этому ключу из обрабатываемого массива будет передаваться в функцию (так же как и у атрибута CB), указанную в значении это словаря.
        """

        def __core_callable(attend: dict, *args, **kwargs):
            newdict = {}
            for k in attend:

                if k in CB_to_keys:
                    t = CB_to_keys[k](
                        __core_callable, attend[k], *args, **kwargs)
                    if t is not None:
                        newdict[k] = t

                elif isinstance(attend[k], dict):
                    recdict = CB(__core_callable, attend[k], *args, **kwargs)
                    if len(attend[k]) == 0:
                        newdict[k] = recdict

                    for k2 in recdict:
                        if k2 == '__value__':
                            newdict[k] = recdict[k2]
                        else:
                            n_k = CB_key((k, k2), *args, **kwargs)
                            if n_k == False:
                                pass
                            elif isinstance(n_k, tuple):
                                if n_k[0] not in newdict:
                                    newdict[n_k[0]] = {}
                                newdict[n_k[0]][n_k[1]] = recdict[k2]
                            else:
                                newdict[n_k] = recdict[k2]

                elif isinstance(attend[k], list):
                    newdict[k] = []
                    for i in attend[k]:
                        newdict[k].append(CB_val(i, *args, **kwargs))

                else:
                    key = CB_key(k, *args, **kwargs)
                    if key:
                        newdict[key] = CB_val(attend[k], *args, **kwargs)

            return newdict

        return CB(__core_callable, self.attend, *args, **kwargs)

    def str_strip(self) -> dict:
        """ Убирает пробелы по бокам у ключей и строковых значений """

        def cb_strip(string: _T.Union[tuple, str]) -> _T.Union[tuple, str]:
            if isinstance(string, tuple):
                return (string[0].strip(), string[1].strip())
            elif isinstance(string, str):
                return string.strip()
            else:
                return string

        return self.core(CB_key=cb_strip, CB_val=cb_strip)

    def path_common(self, allow: bool = False) -> dict:
        """ Преобразовывает значения в файловый путь

        Args:
            allow (bool, optional): Начинать с первого уровня или искать target_key и после него преобразовывать до un_target_key
        """

        target_key = "path"
        un_target_key = "__path"

        def cb_val(attend, fromPath: rPath, allow: bool):
            if allow:
                return copy(fromPath).merge(attend)
            return attend

        def callback(cb_core: _T.Callable, attend: dict, fromPath: rPath, allow: bool):
            if allow:
                # attend['.'] = ''
                if 'common' in attend:
                    fromPath = copy(fromPath).merge(attend['common'])
                    del attend['common']

            return cb_core(attend, fromPath, allow)

        cb_keys = {
            'common': lambda cb, val, *args, **kwargs: val,

            target_key: lambda cb_core, attend, fromPath, allow: callback(cb_core, attend, fromPath, True),
            un_target_key: lambda cb_core, attend, fromPath, allow: callback(cb_core, attend, fromPath, False)
        }

        return self.core(CB=callback, CB_val=cb_val, CB_to_keys=cb_keys, fromPath=rPath(), allow=allow)

    def rDict_to_value(self) -> dict:
        """ Преобразовывает класс rDict в класс его значения """

        def cb_val(attend):
            if isinstance(attend, rDict):
                return attend.attend
            return attend

        return self.core(CB_val=cb_val)

    def path_to_str(self) -> dict:
        """ Преобразовывает классы rPath and pathlib.Path в строковое представление """

        def cb_val(attend):
            if isinstance(attend, (pa.Path, rPath)):
                return str(attend)
            return attend

        def cb_key(key):
            if key == '.':
                return False
            return key

        return self.core(CB_val=cb_val, CB_key=cb_key)


def gen_user_workspace(initFile: _T.Union[str, None] = None, joinPath: _T.Union[str, None] = None):
    """ Помогает выбрать пользователю рабочаю область.

    Example:
        gen_user_workspace(__file__, 'workdir/../no/../workspace')

        Equivalent:
            os.path.abspath(os.path.dirname(__file__) + 'workdir/../no/../workspace')

    Args:
        initFile (str, optional): Путь до исполняемого файла __file__.
        joinPath (str, optional): Путь до папки проекта относительно исполняемого файла.

    """

    initPath = os.getcwd() if initFile is None else os.path.dirname(initFile)

    if joinPath is not None:
        initPath = os.path.abspath(os.path.join(initPath, joinPath))

    return initPath


def convert_base(num: _T.Union[str, int], from_base: int = 10, to_base: int = 10) -> str:
    """ Перевод числа из одной системы счисления в другую. Максимум 36 разрядная система.

    Args:
        num ([str, int]): Число для перевода
        from_base (int, optional): Из какой системы. Defaults to 10.
        to_base (int, optional): В какую систему. Defaults to 10.

    Returns:
        str: Строковое представление переведенного числа

    """

    assert from_base > 0 and to_base > 0, 'Разрядность системы не может равняться 0'

    number = num
    if isinstance(num, str):
        number = int(num, from_base)

    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    if number < to_base:
        return alphabet[number]
    else:
        return convert_base(number // to_base, 10, to_base) + alphabet[number % to_base]


# NO TESTS
def call_restriction(count: int):
    """ Декоратор. Предотвращает вызов функции более 1 раза """

    @functools.wraps(call_restriction)
    def wrapper(func: types.FunctionType):

        logger.debug(f'На функцию {func.__module__}.{func.__name__} применен декоратор ограничивающий количество вызовов')

        @functools.wraps(func)
        def inner(*args, **kwargs):

            inner.count -= 1
            if inner.count < 0:
                logger.debug(f'Функция {func.__module__}.{func.__name__} пропущена')
                return

            result = func(*args, **kwargs)

            if result is not None:
                logger.error(f'Функция {func.__module__}.{func.__name__} вернула значение отличное от None')
                raise ValueError(f'Функция обернутая в декоратор {call_restriction.__module__}.{call_restriction.__name__} не должна возвращать данные.')

        inner.count = count

        return inner
    return wrapper


def short_text(string: str, maxLength: int = 50) -> str:

    logger.log(0, f'Сокращение строки "{string}" до {maxLength} символов')

    if len(string) > maxLength:
        string = f"{string[:(maxLength // 2)]}...{string[(maxLength // 2 * -1):]}"

    string = re.sub(r'[\s]+', ' ', string)

    logger.log(0, f'Результат: "{string}"')

    return string


def lead_time(func: _T.Callable):
    """ Декоратор для подсчета времени выполнения функции """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        start_time = time.monotonic()

        result = func()

        end_time = time.monotonic()

        print(datetime.timedelta(seconds=end_time - start_time))

        return result

    return wrapper


def keyByValue(array: dict, value: _T.Any) -> _T.Any:
    return list(array.keys())[list(array.values()).index(value)]


def split_list_by_indexes(array: list, indexes: list[int]):
    """ Разделить массив по индексам """

    arrays = []

    startpoint = indexes[0]
    endpoint = indexes[1]

    endpoint += 1

    arrays.append(
        array[:startpoint]
    )

    if endpoint == len(array):
        arrays.append(
            array[startpoint:]
        )
        arrays.append(
            []
        )

    else:
        arrays.append(
            array[startpoint:-(len(array) - endpoint)]
        )

        arrays.append(
            array[-(len(array) - endpoint):]
        )

    logger.debug(f'Разбиение списка длиной {len(array)} по индексам {indexes}. Результат: 3 списка длинной: {[len(i) for i in arrays]}')

    return arrays


def debugmod(onlyDebug: bool = True, anywaySkip: bool = False):
    """ Декоратор для функций, которые будут вызываться только при включенном или выключенном debug режиме

    Args:
        onlyDebug (bool): Если True, функция будет запущена только при включенном debug режиме
            Если False, то только при выключенном  debug режиме

        anywaySkip (bool): Пропустить при любой настройке debug режима

    """

    from . import main

    def wrapper(func: _T.Callable):

        if ((onlyDebug and main.__debug_mod__) or (not onlyDebug and not main.__debug_mod__)) and not anywaySkip:
            return func

        if anywaySkip:
            logger.warning(f'Включен режим anywaySkip для функции "{func.__name__}"')

        def mask_func(*args, **kwargs):
            logger.debug(f'Вызов функции "{func.__name__}" был пропущен, так {"не" if onlyDebug else ""} включен режим отладки')

        return mask_func

    return wrapper


class IdentifierAssignment(object):
    """ Присвоение некому объекту идентификатора с 1 """

    items: list[int]

    def __init__(self) -> None:
        self.items = []

    def id(self, obj: _T.Any) -> int:
        """ Присвоение некому объекту идентификатора с 1

        Args:
            obj (_T.Any): Некий объект

        """

        objHash = hash(obj)

        if objHash not in self.items:
            self.items.append(objHash)

        return self.items.index(objHash)


def len_generator(generator: _T.Generator):
    """ Функция для определения длины генератора """

    return len(list(generator))
