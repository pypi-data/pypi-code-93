from typing import List


class Error(Exception):
    pass


class MigrateError(Error):
    def __init__(self, message: str, script_name: str):
        self.message = message
        self.script_name = script_name

    def __str__(self):
        return f"{self.message}"


class IncorrectlyExecutedScriptsError(Error):
    def __init__(self, scripts: List):
        self.__scripts = scripts

    def __str__(self):
        message = 'Миграция невозможна, т.к. есть ошибки после прошлой миграции у скриптов:'
        for i in self.__scripts:
            message += f' "{i}"'
        return message
