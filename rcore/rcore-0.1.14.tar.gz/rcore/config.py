""" Модуль работы с конфигурацией приложения """

from __future__ import annotations

import typing as _T
from copy import copy, deepcopy
from dataclasses import dataclass, field
from glob import glob

import rlogging

from rcore import exception as ex
from rcore import rtype
from rcore.rpath import rPath, rPaths
from rcore.utils import rDict, rRecursion

logger = rlogging.get_logger('mainLogger')


@dataclass
class CfgRule(object):
    """ Правило для ключей keys из некого словаря, состоящее из под-правил children """

    description: str
    keys: list[str]
    validator: rtype.Validator
    children: list[CfgRule] = field(default_factory=list)


class ConfigEngine(object):
    """ Интерфейс обработки файлов конфигурации для создания валидной конфигурации приложеня

    Raises:
        FileNotFoundError: Попытка прочитать несуществующий именованный файл конфигурации.
        TypeError: Прочтенный файл конфигурации содержал не словарь данных.

    """

    prepared: bool
    config: rDict
    filesFrom: dict
    namedFiles: dict
    DirectConfig: dict

    rules: list[CfgRule] = []

    def __init__(self) -> None:
        self.prepared = False

        self.filesFrom = {}
        self.namedFiles = {}
        self.DirectConfig = {}

    def init(self, filesFrom: dict = {}, namedFiles: dict = {}, config: dict = {}):
        """ Инициализация файлов конфигурации """

        self.filesFrom = filesFrom
        self.namedFiles = namedFiles
        self.DirectConfig = config

    def preparation(self):
        """ Специфичный для каждого дочернего класса метод.

        Адаптирует конфигурацию под набор правил.

        """

        self.merge()
        self.use_rule()
        self.path_common()
        self.save()
        self.prepared = True

    def merge(self):
        """ Слияние инициализованных файлов """

        self.config = rDict()
        all_paths = list()

        for fr in self.filesFrom:
            all_paths += [_x for _l in [
                glob(str(rPath(i, fromPath=fr)), recursive=True) for i in self.filesFrom[fr]
            ] for _x in _l]

        namedFiles = {}

        for name in self.namedFiles:
            namedFiles[name] = rPath(self.namedFiles[name])
            if namedFiles[name].check():
                all_paths.append(str(namedFiles[name]))
            else:
                namedFiles[name].create()

        checkPaths = []

        for path in all_paths:
            if path in checkPaths:
                continue
            checkPaths.append(path)

            logger.debug(f'Для конфигурации задействован файл "{path}"')

            fileConfig = rPath(path).parse()
            if isinstance(fileConfig, dict):
                self.config.merge(fileConfig, True)
            else:
                rtype.print_error('json in config file', fileConfig, [dict])

        self.config.merge(self.DirectConfig)

        self.config.set(namedFiles, ['__dev__', 'config_NamedFiles'])
        self.config.set(all_paths, ['__dev__', 'config_files'])
        self.config.set(deepcopy(rPaths.paths), ['__dev__', 'path'])

        self.config = rDict(rRecursion(self.config.attend).str_strip())
        logger.info(
            f"Initialized { len(all_paths) } configuration files"
        )

    def use_rule(self):
        """ Проверка конфигурации по правилам self.rules """

        @rtype.strict
        def __recursion(rule: CfgRule, attend: dict) -> dict:
            """ Применение правил на ключи и активация дочерних правил

            Args:
                attend (dict): Исходный словарь

            Returns:
                dict: Новый словарь

            """

            if len(rule.keys) > 1 and dict in rule.validator.types:
                prepAttend = rDict(attend)
                prepAttend.merge_keys(rule.keys[0], rule.keys[1:], True)
                newAttend = prepAttend.attend
            else:
                newAttend = attend

            if rule.keys[0] not in newAttend:
                newAttend[rule.keys[0]] = rule.validator.default
            else:
                newAttend[rule.keys[0]] = rule.validator.check(newAttend[rule.keys[0]])

            for subRule in rule.children:
                newAttend[rule.keys[0]] = __recursion(subRule, newAttend[rule.keys[0]])

            return newAttend

        attend = self.config.attend

        for rule in self.rules:
            attend = __recursion(rule, attend)

        self.config.attend = attend

    def path_common(self):
        """ Преобразование строковые пути в rPath """

        self.config = rDict(rRecursion(self.config.attend).path_common())

    def save(self):
        """ Сохранение готовой конфигурации в кеш """

        rPath('used-config.json', fromPath='cache').dump(self.config)

    @classmethod
    def docs_rules(self) -> str:
        """ Документировани правил для настроек в конфигурации """

        @rtype.strict
        def __inner(rule: CfgRule, tab: int) -> str:
            settingsDocsText = '    ' * tab

            settingsDocsText += '%-10s' % rule.keys[0]
            settingsDocsText += ' : ' + rule.description if rule.description is not None else ''

            settingsDocsText += '\n'

            for subRule in rule.children:
                settingsDocsText += __inner(subRule, tab + 1)

            return settingsDocsText

        if self.rules:
            settingsDocsText = ''

            for rule in self.rules:
                settingsDocsText += __inner(rule, 0)

        else:
            settingsDocsText = 'У данной программы нет конфигурации.'

        return settingsDocsText


class rcoreConfig(ConfigEngine):
    """ Пример надстроки движка конфигурации """

    rules = [
        CfgRule(
            'Пример использования правил',
            ['key', 'keys'],
            rtype.Validator(str, [], 'default value'),
        )
    ]

    def preparation(self):
        self.merge()

        self.use_rule()

        self.save()

        self.prepared = True


class CfEngine(object):
    """ Интерфейс для взаимодействия с конфигурацией, которая является производной от ConfigEngine """

    core: ConfigEngine

    def __init__(self, coreType: _T.Type[ConfigEngine]):
        """ Инициализация объекта

        Args:
            coreType (_T.Type[ConfigEngine]): Тип ядра конфигурации, наследуемое от ConfigEngine

        """

        core = coreType()

        self.core = core
        self.init = core.init
        self.preparation = core.preparation

    def get(self, dictPath: list, default: _T.Any = Exception) -> _T.Any:
        """ Получение значения конфигурации по ключам dictPath

        Args:
            dictPath (list, optional): Ключи словарей и списков до искомого значения.
            default (_T.Any, optional): Значение по умолчанию, если один из ключей dictPath не будет найден. Defaults to Exception.

        Raises:
            ex.errors.NotInitConfig: Конфигурация приложения не была инициализирована.

        Returns:
            _T.Any: Искомое значение

        """

        if self.core.prepared:
            return self.core.config.get(dictPath, default)

        else:
            raise ex.errors.NotInitConfig from None

    def setting(self, *args: str) -> _T.Any:
        """ Получение значения настроек

        Returns:
            _T.Any: Искомая настройка

        """

        return self.get(['setting', *args])

    def path(self, *args: str) -> rPath:
        """ Получение некого пути

        Returns:
            rPath: Искомая путь

        """

        return copy(self.get(['path', *args]))

    def file(self, name: str) -> rPath:
        """ Получение пути именованного файла конфигурации

        Args:
            name (str): Идентификатор именованного файла

        Raises:
            ex.errors.NotInitConfigFile: Именованный файл не был инициализированн.

        Returns:
            rPath: Путь до именованного файла конфигурации

        """

        try:
            return self.get(['__dev__', 'config_NamedFiles', name])

        except ex.errors.ItemNotFound:
            raise ex.errors.NotInitConfigFile(name) from None


cf = CfEngine(rcoreConfig)


class CfEditNamedFile(object):
    """ Класс для редактирования именованного файла конфигурации с помощью структуры: with ... as : """

    __slots__ = ('cf', 'fileName', 'config')

    cf: CfEngine
    fileName: str
    config: rDict

    def __init__(self, cf: CfEngine, fileName: str):
        """ Инициализация

        Args:
            cf (CfEngine): Инициализированный обработчик конфигурации
            fileName (str): Идентификатор именованного файла

        """

        self.cf = cf
        self.fileName = fileName

    def __enter__(self):
        logger.debug(f'Редактирование именованного файла конфигурации "{self.fileName}"')

        configFile = self.cf.file(self.fileName)

        if not configFile.check():
            configFile.create()

        self.config = rDict(configFile.parse())

        return self.config

    def __exit__(self, type, value, traceback):
        logger.debug('Файла конфигурации успешно изменен')

        self.cf.file(self.fileName).dump(self.config)

        self.cf.preparation()
