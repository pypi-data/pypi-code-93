"""
Модуль миграции БД MYSQL
"""
from enum import Enum
from migration.errors import MigrateError, IncorrectlyExecutedScriptsError
from typing import List, Optional
from pymysql import Connection
from pymysql.cursors import DictCursor
from config import Configuration
from subprocess import run as run_shell, PIPE
import re
from inspect import getframeinfo, currentframe
from os import remove, listdir, getenv
from os.path import dirname, abspath, exists as path_exists, join as path_join

_path_to_module = dirname(abspath(getframeinfo(currentframe()).filename))


class StatusMigration(Enum):
    Success = 'Success'
    Error = 'Error'
    Execution = 'Execution'


class Version:
    def __init__(self, version: str):
        match = re.match(r"v?[0-9]+\.[0-9]+\.[0-9]+", version)
        if not match:
            raise RuntimeError(f"Неверный формат версии {version}")
        version = match.group(0).replace('v', '').split('.')
        self.__major = int(version[0])
        self.__minor = int(version[1])
        self.__maintenance = int(version[2])

    def __lt__(self, other):
        if type(other) != Version:
            raise RuntimeError("Сравнение возможно только с классом Version")
        if self.__major == other.__major:
            if self.__minor == other.__minor:
                return self.__maintenance < other.__maintenance
            else:
                return self.__minor < other.__minor
        else:
            return self.__major < other.__major

    def __le__(self, other):
        if not self.__eq__(other):
            return self.__lt__(other)
        return True

    def __ge__(self, other):
        if not self.__eq__(other):
            return self.__gt__(other)
        return True

    def __gt__(self, other):
        if type(other) != Version:
            raise RuntimeError("Сравнение возможно только с классом Version")
        if self.__major == other.__major:
            if self.__minor == other.__minor:
                return self.__maintenance > other.__maintenance
            else:
                return self.__minor > other.__minor
        else:
            return self.__major > other.__major

    def __eq__(self, other):
        if type(other) != Version:
            raise RuntimeError("Сравнение возможно только с классом Version")
        return (self.__major == other.__major) and (self.__minor == other.__minor) and \
               (self.__maintenance == other.__maintenance)

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def get_version(self):
        return f"{self.__major}.{self.__minor}.{self.__maintenance}"

    @classmethod
    def from_script_name(cls, script_name: str):
        return Version(re.search(r'(v)([0-9]+\.[0-9]+\.[0-9]+)', script_name).group(2))


class MigrationDB:
    """Класс для миграции БД MYSQL"""

    __MASK_VERSION = r"[0-9]{1,}\.[0-9]{1,}\.[0-9]{1,}[a,b,pre]?"
    __MIGRATION_TABLE = 'migration'

    def __init__(self):
        self.__logger = None
        self.__db_user = None
        self.__db_password = None
        self.__connection = None
        config = Configuration()
        self.__logger = config.logging.get_logger('Migration')
        self.__logger.debug(f'Получен объект {config}')
        self.__logger.debug(f'Получен объект {self.__logger}')

        self.__connection = Connection(host=config.DB['host'], user=config.DB['migration']['user'],
                                       password=config.DB['migration']['password'], port=config.DB['port'],
                                       db=config.DB['DB_name'], autocommit=True)
        self.__logger.debug(f'Получен объект {self.__connection}')

        self.__logger.debug(f'Полный путь до модуля: {_path_to_module}')

        self.__db_user = config.DB['migration']['user']
        self.__db_password = config.DB['migration']['password']
        self.__db_name = config.DB['DB_name']
        self.__rollback_on_error = config.DB['migration']['rollback_on_error']

        self.__path_scripts = getenv('MIGRATION_SCRIPTS')
        if not self.__path_scripts:
            self.__logger.warning('Переменная "MIGRATION_SCRIPTS" не задана. Будет использоваться стандартный путь')
            self.__path_scripts = path_join(_path_to_module, 'SQL')

        if not self.__check_table_migration__():
            self.__create_table_migration__()

        self.__DB_version = self.__get_version_db__()

        self.__logger.debug(f'Инициализирован объект {str(self)}')
        del config

    def __del__(self):
        if path_exists(f'{path_join(_path_to_module, "migration.log")}'):
            remove(f'{path_join(_path_to_module, "migration.log")}')
        del self.__logger
        del self.__db_user
        del self.__db_password
        if self.__connection:
            self.__connection.close()
        del self.__connection

    def __get_version_db__(self) -> Optional[Version]:
        cursor = self.__connection.cursor(DictCursor)
        cursor.execute(f"SELECT * FROM `{MigrationDB.__MIGRATION_TABLE}` ORDER BY `id_migration` DESC LIMIT 1")
        version = cursor.fetchone()
        if version:
            return Version(version['version_script'])
        return version

    def __check_error_migration__(self):
        cursor = self.__connection.cursor(DictCursor)
        try:
            cursor.execute(f"select * from `{self.__MIGRATION_TABLE}` "
                           f"where `status_migrate` = '{StatusMigration.Error.value}' or "
                           f"`status_migrate` = '{StatusMigration.Execution.value}'")
            error_migrations = cursor.fetchall()
            if error_migrations:
                scripts_error = [i['name_script'] for i in error_migrations]
                raise IncorrectlyExecutedScriptsError(scripts_error)
        except IncorrectlyExecutedScriptsError as e:
            self.__logger.error(str(e))
            raise
        finally:
            cursor.close()

    def __check_table_migration__(self) -> bool:
        cursor = self.__connection.cursor(DictCursor)
        try:
            cursor.execute(f'Show tables')
            tables = cursor.fetchall()
            for i in tables:
                if MigrationDB.__MIGRATION_TABLE in i.values():
                    return True
            return False
        finally:
            cursor.close()

    def __create_table_migration__(self):
        with open(path_join(_path_to_module, 'migration_table.sql'), 'r') as file_script:
            script = file_script.read()
            script = script.replace('`table_name`', f'`{MigrationDB.__MIGRATION_TABLE}`')

            cursor = self.__connection.cursor()
            try:
                cursor.execute(script)
            finally:
                cursor.close()

    def __check_names_migrate_scripts__(self, scripts: List[str]):
        re_mask_script_name = r'^[0-9]{1,}_v[0-9]{1,}\.[0-9]{1,}\.[0-9]{1,}_[a-zA-Z_0-9\.]{1,}\.sql$'
        self.__logger.debug(f'Патерн проверки название скрипта: {re_mask_script_name}')
        for i in scripts:
            match = re.match(re_mask_script_name, i)
            if not match:
                raise RuntimeError(f"Неверно назван файл миграции: {i}")

    def __sort__(self, sorting_elements: List[str]) -> List[str]:
        """
        Метод сортирует скрипты миграции по приоритету скриптов

        :param sorting_elements: список элементов, которые нужно отсортировать.
        :return: возвращает отсортированные скрипты
        """
        self.__logger.debug('Сортировка скриптов по номеру')
        re_mask_priority_script = r'^[0-9]{1,}'
        sorting_elements = sorted(sorting_elements,
                                  key=lambda item: int(re.match(re_mask_priority_script, item).group(0)))
        self.__logger.debug(f"Отсортированые элементы {str(sorting_elements)}")
        return sorting_elements

    def __filter_scripts_by_version__(self, filter_version: Version, scripts: List[str]) -> List[str]:
        """
        Метод фильтрует скрипты, которые нужно прогнать для указанной версии

        :param filter_version: версия приложения
        :param scripts: список скриптов
        :return: скрипты которые нужны для текущей версии
        """
        for i, name in enumerate(scripts):
            version_script = Version.from_script_name(name)
            if filter_version < version_script:
                scripts = scripts[:i]
                break
        self.__logger.debug(f'Получены скрипты после прогона фильтра по версии: {scripts}')
        return scripts

    def __filter_scripts_by_db_version(self, filter_version: Version, scripts: List[str]) -> List[str]:
        """
        Метод фильтрует скрипты, которые нужно прогнать для текущей версии бд

        :param filter_version: версия приложения
        :param scripts: список скриптов
        :return: скрипты которые нужны для текущей версии
        """

        if self.__DB_version:
            scripts = scripts[scripts.index(next(i for i in scripts if filter_version.get_version in i)) + 1:]
        return scripts

    def __rollback_script(self, script_name):
        self.__logger.info('Выполнения отката скрипта, после ошибки миграции')
        self.__logger.debug(f'Откат скрипта: {script_name}')
        run_shell([f'mysql -u "{self.__db_user}" -p"{self.__db_password}" {self.__db_name} --html '
                   f'-e "source {path_join(self.__path_scripts, "rollback", script_name)}"'],
                  stderr=PIPE, shell=True)
        self.__logger.info(f'Откат выполнен')

    def __migrate_script__(self, script_name: str):
        """
        Метод запуска скрипта миграции

        Метод в зависимости от платформы запускает скрипт миграции.
        :param script_name: имя скрипта миграции
        """
        cursor = self.__connection.cursor()
        priority = re.search(r'^[0-9]+', script_name).group(0)
        version = Version.from_script_name(script_name).get_version
        status = StatusMigration.Execution.value
        try:
            self.__logger.info(f'Выполнения скрипта миграции: {script_name}')
            cursor.execute(f"Insert into `{self.__MIGRATION_TABLE}` (`priority_script`, `version_script`, "
                           f"`name_script`, `status_migrate`) values ({priority}, '{version}', '{script_name}', "
                           f"'{status}')")

            complete_command = run_shell([f'mysql -u "{self.__db_user}" -p"{self.__db_password}" {self.__db_name} '
                                          f'--abort-source-on-error --html '
                                          f'-e "source {path_join(self.__path_scripts, "migration", script_name)}"'],
                                         stderr=PIPE, shell=True)
            status = StatusMigration.Success.value
            self.__logger.info(f'Скрипт миграции завершился с кодом: {complete_command.returncode}')
            if complete_command.returncode:
                status = StatusMigration.Error.value
                raise MigrateError(complete_command.stderr.decode('utf-8'), script_name)
        except MigrateError as e:
            self.__logger.error(str(e))
            if self.__rollback_on_error:
                self.__rollback_script(script_name)
            raise
        finally:
            cursor.execute(f"Update `{self.__MIGRATION_TABLE}` set `status_migrate` = '{status}'"
                           f"where `name_script` = '{script_name}'")
            cursor.close()

    def migrate(self, version: Version):
        """
        Метод запуска миграции

        Метод проверяет прогнанные скрипты и прогонает те, которые не были прогнаны.
        """
        self.__check_error_migration__()

        scripts = listdir(path_join(self.__path_scripts, 'migration'))
        self.__logger.debug(f'Получен список скриптов мигрирования: {str(scripts)}')
        if scripts:
            self.__check_names_migrate_scripts__(scripts)

            scripts = self.__sort__(scripts)

            scripts = self.__filter_scripts_by_version__(version, scripts)

            scripts = self.__filter_scripts_by_db_version(self.__DB_version, scripts)

            if scripts:
                self.__logger.info('Начала миграции')
                for i in scripts:
                    self.__migrate_script__(i)
                self.__logger.info('Миграции БД выполнена')
            else:
                self.__logger.info('БД не нуждается в миграции')
        else:
            self.__logger.info('Скрипты миграции отсутствуют')


if __name__ == '__main__':
    m = MigrationDB()
    m.migrate(Version('2.2.0'))
    del m
