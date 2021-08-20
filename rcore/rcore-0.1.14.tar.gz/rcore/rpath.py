from __future__ import annotations

import functools
import os
import pathlib as pa
import shutil
import typing as _T
from glob import glob

import rlogging
import yaml

from rcore import exception as ex
from rcore import rtype

logger = rlogging.get_logger('mainLogger')


class RootPaths(object):
    """ Класс корневых путей приложения """

    isInit: bool
    paths: dict[str, dict[str, pa.Path]]

    def __init__(self):
        self.isInit = False
        self.paths = {}

    def init(self,
             userPath: pa.Path,
             projectPath: pa.Path,
             corePath: pa.Path,
             cacheFolderName: _T.Optional[str] = None,
             logsFolderName: _T.Optional[str] = None
             ):
        """ Инициализация корневых путей приложения

        Args:
            userPath (pa.Path): Абсолютный путь до директории, которую указал пользователь
            projectPath (pa.Path): Абсолютный путь до директории - надстройки над rcore
            corePath (pa.Path): Абсолютный путь до директории rcore
            cacheFolderName (pa.Path): Абсолютный путь до директории rcore
            cacheFolderName (_T.Optional[str], optional): Имя папки - кеша приложения. Defaults to None.
            logsFolderName (_T.Optional[str], optional): Имя папки - логов приложения. Defaults to None.

        """

        logger.info('Инициализация путей')

        self.isInit = True
        self.paths = {
            'core': {
                '.': corePath,
                'source': corePath / 'source'
            },
            'app': {
                '.': projectPath,
                'source': projectPath / 'source'
            },
            'project': {
                '.': userPath,
                'source': userPath / 'source'
            },
            'cwd': {
                '.': pa.Path.cwd()
            },
            'cache': {
                '.': userPath / 'cache' if cacheFolderName is None else userPath / cacheFolderName
            },
            'logs': {
                '.': userPath / 'cache/logs' if logsFolderName is None else userPath / logsFolderName
            },
        }

        logger.debug('Конечные точки путей: {}'.format(
            self.paths
        ))

    def get(self, key: str) -> pa.Path:
        """ Получение пути до искомой точки

        Args:
            key (str): Ключ до точки. Если нужно получить подпапку основной директории, то ключи соединены точкой.

        Returns:
            str: Абсолютный путь до искомой точки.

        """

        if not self.isInit:
            raise ex.errors.NotInitPathError()

        keys = key.split('.')

        if len(keys) == 1:
            return self.paths[key]['.']
        elif len(keys) == 2:
            return self.paths[keys[0]][keys[1]]
        else:
            raise ex.errors.DeveloperIsShitError()

    def points(self) -> list[str]:
        """ Создание списка "якорей" """

        if not self.isInit:
            raise ex.errors.NotInitPathError()

        points = []
        for point in self.paths:
            points.append(point)
            for subPoints in self.paths[point]:
                if subPoints != '.':
                    points.append(point + '.' + subPoints)

        return points


rPaths = RootPaths()


def pathGenerate(fromPath: _T.Union[str, None] = None, path: str = '') -> pa.Path:
    """ Поиск якорей в строковых путях.

    Якорь, слово формата __point__, где point - исходная точка из RootPaths.paths

    Args:
        path (str): Путь

    Returns:
        pa.Path: Путь с учетом якорей
    """

    if fromPath is None:
        fromPath = 'project'

    for point in rPaths.points():
        strPoint = '__{0}__'.format(
            point
        )
        splitPath = path.split(strPoint)
        if len(splitPath) > 1:
            fromPath = point
            path = splitPath[-1].strip()

            if len(path) > 0 and path[0] == '/':
                path = path[1:]

    return rPaths.get(fromPath).joinpath(path).resolve()


def arcmerge(fromPath: str, toPath: str) -> str:
    """ Обратная от слияния путей. Вычисляет разницу между конечной и начальной точками.

    Args:
        toPath (str): Конечная точка

    Returns:
        str: Строка, с которой надо слить начальную точку, чтобы попасть в конечную

    """

    if os.path.splitext(fromPath)[1]:
        fromPath, _ = os.path.split(fromPath)

    path_list_1 = [i for i in fromPath.split('/') if i != '']
    path_list_2 = [i for i in toPath.split('/') if i != '']
    path_list_new: list[str] = []

    if len(path_list_1) - len(path_list_2) > 0:
        path_list_new = ['..'] * (len(path_list_1) - len(path_list_2))

    noParent = True
    for i in range(len(path_list_2)):
        if i < len(path_list_1):
            if not path_list_1[i] == path_list_2[i] or not noParent:
                path_list_new.insert(0, '..')
                path_list_new.append(path_list_2[i])
                noParent = False
        else:
            path_list_new.append(path_list_2[i])
    return '/'.join(path_list_new)


class rPath(object):

    def __copy__(self):
        return rPath(str(self.path))

    def __eq__(self, t):
        return str(self.path) == str(t)

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return str(self.path)

    def __hash__(self):
        return str(self).__hash__()

    extension: _T.Union[str, bool]
    name: str
    path: pa.Path

    def __init__(self, path: _T.Union[str, None] = None, fromPath: _T.Union[str, None] = None):
        self.init(path, fromPath)

    def init(self, path: _T.Union[str, None] = None, fromPath: _T.Union[str, None] = None):

        rtype.optional('path', path, [str])
        rtype.optional('fromPath', fromPath, [str])

        isDir = False
        if isinstance(path, str) and path[-1] == '/':
            isDir = True

        if path is None:
            self.path = pathGenerate(fromPath)
        else:
            self.path = pathGenerate(fromPath, path)

        fileNameNoExtension, self.extension = os.path.splitext(str(self))
        _, self.name = os.path.split(fileNameNoExtension)

        if isDir:
            self.name += self.extension
            self.extension = False
        elif self.extension == '':
            self.extension = False

    def merge(self, *args: str) -> rPath:
        """ Слияние пути с получеными строками.

        Args:
            key (str): Строки, которые будут изменять путь.

        Returns:
            rPath: Ссылка на объект

        """

        MainPath = self.path
        if self.is_file():
            MainPath = self.parent().path

        for plusPath in args:
            MainPath = MainPath.joinpath(plusPath).resolve()

        self.init(str(pathGenerate(None, str(MainPath))))
        return self

    @functools.wraps(arcmerge)
    def arcmerge(self, toPath: _T.Union[rPath, pa.Path, str]) -> str:

        if not isinstance(toPath, str):
            toPath = str(toPath)

        return arcmerge(str(self), toPath)

    def is_file(self):
        """ Ссылается ли путь на файл """

        if self.extension is False:
            return False

        return True

    def check(self):
        """ Существует ли файл или папка по пути """

        if self.is_file() and self.path.is_file():
            return True
        if not self.is_file() and self.path.is_dir():
            return True
        return False

    def create(self):
        """Создать файл или папку по пути"""

        if self.is_file():
            logger.debug(f'Created file - "{self}"')
            directory = str(self.parent())
        else:
            logger.debug(f'Created directory - "{self}"')
            directory = self

        try:
            os.makedirs(str(directory))

        except FileExistsError:
            pass

        if self.is_file() and not self.check():
            with open(str(self), 'w') as f:
                pass

        return self

    def write(self, text: str, mode: str):
        """Запись в файл по пути. Аналог функции open.

        Args:
            text (str): Текст для записи
            mode (str): Мод записи

        """

        if mode == 'w' and not self.check():
            self.create()

        logger.debug(f'Write text: \'{text}\' in file: "{self}"')

        if self.is_file():
            with open(str(self), mode) as f:
                f.write(text)
        else:
            raise ex.errors.DirNotFile(str(self))

    def read(self):
        """Прочитать файл по пути"""

        if self.is_file():
            return self.path.read_text()
        else:
            raise ex.errors.DirNotFile(str(self))

    def delete(self, cleartree: bool = False):
        """Прочитать файл или папку по пути"""

        try:
            if self.is_file():
                self.path.unlink()

                logger.debug(f'Delete file - "{str(self)}"')
            else:
                shutil.rmtree(str(self))
        except FileNotFoundError:
            pass

        if cleartree:
            papa = self.parent()
            papawalk = papa.walk()
            if len(papawalk) == 1 and len(papawalk[0]['files']) == 0 and len(papawalk[0]['folders']) == 0:
                papa.delete(True)

    def parse(self) -> _T.Any:

        if self.extension == '.json':
            from rcore.utils import rJson

            return rJson().parse(self.read())

        elif self.extension == '.yaml':
            return yaml.safe_load(self.read())

        else:
            raise ex.errors.DeveloperIsShitError('why?')

    def dump(self, variable: _T.Any):
        from .utils import rJson

        if not self.check():
            self.create()
        self.write(rJson().dump(variable), 'w')

    def parent(self, lvl: int = 0) -> rPath:
        return rPath(str(self.path.parents[lvl]))

    def walk(self, thisfolder: bool = False) -> list[dict[str, _T.Union[rPath, list[str]]]]:
        """Аналог os.walk.

        Args:
            countFolders (int, optional): [description]. Defaults to 0.

        Return:
            list[dict[str, [rPath, list[str]]]]

        """

        if self.is_file():
            raise ex.errors.FileNotDir(str(self))

        SubFolders: list[dict[str, _T.Union[rPath, list[str]]]] = []
        walks = list(os.walk(str(self)))
        for walk in walks:
            SubFolders.append({
                'path': rPath(walk[0]),
                'folders': walk[1],
                'files': walk[2],
            })
            if thisfolder:
                break
        return SubFolders

    def copy_file(self, targetPath: _T.Union[str, rPath]):
        """ Скопировать файл в новый путь """

        if isinstance(targetPath, str):
            targetPath = rPath(targetPath)

        targetPath.parent().create()

        shutil.copyfile(str(self), str(targetPath))


class rPathFile(rPath):
    """ Класс предназначен для инициализации через папку """

    def __init__(self, path: _T.Union[str, None] = None, fromPath: _T.Union[str, None] = None):
        self.init(path, fromPath)

        if not self.is_file():
            self.extension = ''


class rPathDir(rPath):
    """ Класс предназначен для инициализации через директорию """

    def __init__(self, path: _T.Union[str, None] = None, fromPath: _T.Union[str, None] = None):
        self.init(path, fromPath)

        if isinstance(self.extension, str) and self.extension:
            self.name += self.extension
            self.extension = False


class rPathCopy(object):

    @staticmethod
    def mergedir(mainDir: str,
                 restDirs: list[str],

                 patterns: list = ['*'],
                 recurse: bool = False):
        """ Слить папки restDirs в папку mainDir

        Args:
            mainDir (str): Основная папка
            restDirs (tuple[str]): Папки для слияния
            patterns (list, optional): [description]. Defaults to ['*.*'].
            recurse (bool, optional): [description]. Defaults to False.

        Raises:
            ex.errors.FileNotDir: [description]
            ex.errors.FileNotDir: [description]

        """

        logger.debug(f'Слияние директорий {mainDir} и {restDirs}')

        rMainDir = rPath(mainDir)

        if rMainDir.is_file():
            raise ex.errors.FileNotDir(mainDir)

        if not rMainDir.check():
            rMainDir.create()

        for directory in restDirs:
            rDirectory = rPath(directory)

            if not rDirectory.check():
                raise FileNotFoundError(directory)

            if rDirectory.is_file():
                raise ex.errors.FileNotDir(directory)

            root = str(rDirectory) + '/'

            for walk in rDirectory.walk(not recurse):
                for pattern in patterns:
                    files = glob(str(walk['path']) + '/' + pattern)
                    for file in files:
                        oldFile = rPathFile(file)
                        newFile = rPathFile(str(rMainDir) + '/' + str(oldFile).replace(root, ''))

                        if not newFile.check():
                            newFile.create()
                        newFile.write(oldFile.read(), 'w')
