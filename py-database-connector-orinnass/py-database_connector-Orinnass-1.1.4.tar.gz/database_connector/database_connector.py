from tools import Singleton
# TODO: Обновить библиотеку как появится новая версия
from pymysqlpool.pool import Pool
import pymysql
from config import Configuration
import pandas as pd
from typing import Union, Optional
import warnings


class Connection:
    def __init__(self, connection: pymysql.Connection, pool_connections):
        config = Configuration()
        self.__logger = config.logging.get_logger("Mysql Connection")
        self.__logger.debug(f'Получение подключение к бд {connection}')
        self.__connection: pymysql.Connection = connection
        self.__pool: ConnectionsPool = pool_connections
        del config

    def release(self):
        if self.__connection:
            self.__pool.release(self.__connection)
            self.__connection = None
            self.__logger.debug(f'Возвращение подключения в пул {self.__connection}')

    def __del__(self):
        self.release()

    def read(self, command):
        try:
            self.__logger.warn("Метод является устаревшим. Рекомендуемый метод: read_v3")
            warnings.warn('Метод является устаревшим. Рекомендуемый метод: read_v3', category=DeprecationWarning)
            self.__logger.debug(f'Выполнение запроса: {command}')
            #cursor = connection.cursor()
            #cursor.execute(command)
            #data = cursor.fetchall()
            #cursor.close()
            data = pd.read_sql_query(command, self.__connection)
            return data
        except Exception as e:
            self.__logger.error(str(e), exc_info=True)

    def read_v2(self, command) -> Union[dict, list]:
        try:
            warnings.warn('Метод является устаревшим. Рекомендуемый метод: read_v3', category=DeprecationWarning)
            self.__logger.debug(f'Выполнение запроса: {command}')
            cursor = self.__connection.cursor()
            cursor.execute(command)
            data = cursor.fetchall()
            cursor.close()
            return data
        except Exception as e:
            self.__logger.error(str(e), exc_info=True)

    def read_v3(self, command, first_entry: bool = True, count: Optional[int] = None) -> Union[dict, list]:
        try:
            self.__logger.debug(f'Выполнение запроса: {command}', stack_info=True)
            cursor: pymysql.cursors.Cursor = self.__connection.cursor()
            cursor.execute(command)
            if first_entry:
                data = cursor.fetchone()
            elif count:
                data = cursor.fetchmany(count)
            else:
                data = cursor.fetchall()
            cursor.close()
            return data
        except Exception as e:
            self.__logger.error(str(e), exc_info=True)

    def push(self, command):
        try:
            cursor = self.__connection.cursor()
            self.__logger.debug(f'Выполнение запроса: {command}', stack_info=True)
            cursor.execute(command)
            id_last_write = cursor.lastrowid
            cursor.close()
            return id_last_write
        except Exception as e:
            self.__logger.error(str(e), exc_info=True)


class ConnectionsPool(metaclass=Singleton):
    """Класс управления подключений базы"""

    def __init__(self):
        config = Configuration()
        self.__logger = config.logging.get_logger('Mysql pool connection')
        self.__logger.debug('Создание пула конектов к БД')
        self.__pool = Pool(host=config.DB['host'], user=config.DB["user"],
                           password=config.DB['password'], db=config.DB['DB_name'],
                           port=config.DB["port"], autocommit=True, ping_check=True,
                           max_size=config.DB['max_connections'], min_size=config.DB['min_connections'])
        self.__logger.debug(f'Создан пул конектов к БД {self.__pool}')
        self.__logger.debug('Инициализация пула конектов к БД')
        self.__pool.init()

    def __del__(self):
        self.close()

    def close(self):
        """Метод закрытия подключений"""
        self.__pool.destroy()

    def get_connection(self) -> Connection:
        try:
            self.__logger.debug(f'Размер пула: {self.__pool.current_size}\n'
                                f'Используемые подключения: {self.__pool.inuse_list}\n'
                                f'Неиспользуемые подключения: {self.__pool.unuse_list}')
            mysql_connection = self.__pool.get_conn()
            self.__logger.debug(f"Получено подключение {mysql_connection}")
            connection = Connection(mysql_connection, self.__pool)
            return connection
        except Exception as e:
            self.__logger.error(str(e), exc_info=True)

    def release(self, connection):
        self.__pool.release(connection)
        self.__logger.debug(f'Подключение возвращено в пул {connection}')