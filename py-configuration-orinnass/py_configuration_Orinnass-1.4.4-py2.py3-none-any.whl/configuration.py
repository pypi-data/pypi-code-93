from json.decoder import JSONDecodeError
from logging import INFO, DEBUG, WARNING, ERROR, CRITICAL, NOTSET, root, getLogger, NullHandler, Formatter, \
    StreamHandler, FileHandler, Logger
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from copy import deepcopy
from os import mkdir, getenv
from tools import Singleton
from os.path import join as join_path, exists as exists_path
from typing import List
# from .handlers import DBHandler
import pymysql
from jsonschema import validate as schema_validate, ValidationError
from json import loads as json_loads

root.setLevel(ERROR)
root.addHandler(StreamHandler())

_TIMED_ROTATION = 1
_SIZE_ROTATION = 2

_nameToLevel = {
    'CRITICAL': CRITICAL,
    'ERROR': ERROR,
    'WARN': WARNING,
    'WARNING': WARNING,
    'INFO': INFO,
    'DEBUG': DEBUG,
    'NOTSET': NOTSET,
}
_rotationFileTypes = {
    "TIMED": _TIMED_ROTATION,
    "SIZE": _SIZE_ROTATION
}


class LoggingConfig:
    def __init__(self, config, config_connection_db):
        self.__config = config
        if config_connection_db:
            self.__user_connection = config_connection_db['user']
            self.__password_connection = config_connection_db['password']
            self.__host_connection = config_connection_db['host']
            self.__port_connection = config_connection_db['port']
            self.__db_name_connection = config_connection_db['DB_name']
        self.__generated_loggers: List[str] = []

        self.__general_logger = None
        self.__logger = self.get_logger('LoggingConfig')
        self.__logger.debug(f'Значения параметров:\n'
                            f'config: {config}\n'
                            f'config_connection_db: {config_connection_db}', stack_info=True)
        self.__general_logger = self.get_logger('General')

    def __parse_file_handler__(self, config):
        if 'logging_rotation_type' not in config:
            config['logging_rotation_type'] = None

        if not exists_path(config['directory_log']):
            mkdir(config['directory_log'])

        if _rotationFileTypes[config['logging_rotation_type']] == _TIMED_ROTATION:
            when, interval = config['logging_interval'].split(' ')
            handler = TimedRotatingFileHandler(config['file_name'], when=when, backupCount=config['backup_count'],
                                               interval=int(interval))
        elif _rotationFileTypes[config['logging_rotation_type']] == _SIZE_ROTATION:
            handler = RotatingFileHandler(config['file_name'], maxBytes=int(config['logging_interval']),
                                          backupCount=config['backup_count'])
        else:
            handler = FileHandler(config['file_name'])

        handler.setFormatter(Formatter(config['format_logging']))
        handler.setLevel(config['level_logging'])

        return handler

    def __parse_db_handler(self, config):
        connection = pymysql.Connection(host=self.__host_connection, user=self.__user_connection,
                                        password=self.__password_connection, port=self.__port_connection,
                                        db=self.__db_name_connection, cursorclass=pymysql.cursors.DictCursor)
        # handler = DBHandler(connection, 'logs')
        #
        # handler.setFormatter(Formatter(config['format_logging']))
        # handler.setLevel(config['level_logging'])
        #
        # return handler

    def __parse_console_handler(self, config):
        handler = StreamHandler()
        handler.setLevel(config['level_logging'])
        handler.setFormatter(Formatter(config['format_logging']))

        return handler

    def __generation_handlers__(self, config_handlers):
        handlers = []
        for i in config_handlers:
            if 'enabled_handler' in i and i['enabled_handler'] is False:
                continue

            if i['type_handler'] == "file":
                handlers.append(self.__parse_file_handler__(i))
            elif i['type_handler'] == 'db':
                handlers.append(self.__parse_db_handler(i))
            elif i['type_handler'] == 'console':
                handlers.append(self.__parse_console_handler(i))

        if not handlers:
            handlers.append(NullHandler())

        return handlers

    def get_logger(self, logger_name) -> Logger:
        logger = getLogger(logger_name)

        if logger_name not in self.__generated_loggers:
            parent = None

            config_for_logger_name = None
            for i in self.__config['settings_overload']:
                if i['name_logger'] == logger_name:
                    config_for_logger_name = i['settings']
                    parent = i.get('parent')
                    check_keys = ['level_logging', 'format_logging', 'handlers']
                    for key in check_keys:
                        if key not in config_for_logger_name.keys():
                            config_for_logger_name[key] = self.__config[key]
                    break

            if config_for_logger_name is None:
                config_for_logger_name = deepcopy(self.__config)
                del config_for_logger_name['settings_overload']
            for i in config_for_logger_name['handlers']:
                if 'directory_log' in i:
                    i['file_name'] = join_path(i['directory_log'], f"{logger_name}.log")

                check_keys = ['level_logging', 'format_logging']
                for key in check_keys:
                    if key not in i:
                        i[key] = config_for_logger_name[key]

            logger.setLevel(config_for_logger_name['level_logging'])

            handlers = self.__generation_handlers__(config_for_logger_name['handlers'])

            for i in handlers:
                logger.addHandler(i)

            if parent:
                logger.parent = self.get_logger(parent)
            elif self.__general_logger is not None:
                logger.parent = self.__general_logger

            self.__generated_loggers.append(logger_name)
        return logger


class Configuration(metaclass=Singleton):
    """
    Класс конфигов приложения
    """

    __FILE_TEMPLATE_CONFIG = getenv("TEMPLATE_CONFIG")
    __FILE_CONFIG = getenv("CONFIG_FILE")

    def __init__(self):
        try:
            self.__logger = root
            if not Configuration.__FILE_CONFIG:
                raise KeyError("Не задана переменная файла конфигурации \"CONFIG_FILE\"")
            if not Configuration.__FILE_TEMPLATE_CONFIG:
                raise KeyError("Не задана переменная файла шаблона конфигурации \"TEMPLATE_CONFIG\"")

            self.__path_to_config_file = Configuration.__FILE_CONFIG
            with open(self.__path_to_config_file, 'r') as file_configuration:
                configuration = json_loads(file_configuration.read())

            self.__check_struct_config__()
            for i in configuration:
                self.__logger.debug(f"Конфигурация {i}: {configuration[i]}")
                self.__setattr__(i, configuration[i])
            self.logging = LoggingConfig(self.logging, self.DB)
            self.__logger = self.logging.get_logger("Configuration")
            self.__logger.debug(f"Путь до конфигурации: {self.path_to_config_file}")
            self.__logger.debug(f'Путь до шаблона конфигурации: {Configuration.__FILE_TEMPLATE_CONFIG}')
        except (JSONDecodeError, KeyError, ValidationError) as e:
            self.__logger.error(str(e), exc_info=True)
            exit(1)

    def __getattr__(self, item):
        return self.__dict__.get(item)

    def __check_struct_config__(self):
        self.__logger.info(f'Проверка конфигурации по шаблону')
        with open(Configuration.__FILE_CONFIG, 'r') as config_file:
            with open(Configuration.__FILE_TEMPLATE_CONFIG, 'r') as template_config:
                schema_validate(json_loads(config_file.read()), json_loads(template_config.read()))
                self.__logger.info(f'Проверка конфигурации пройдена')

    @property
    def path_to_config_file(self):
        self.__logger.debug(f'Возвращение значения: {self.__path_to_config_file}', stack_info=True)
        return self.__path_to_config_file
