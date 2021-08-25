from addon.__slashcommand__ import slashcommand
from addon.__entityquery__ import __entityquery__
from addon.__componentbinding__ import __componentbinding__
from addon.__entitybinding__ import __entitybinding__
from addon.__eventbinding__ import __eventbinding__
from addon.__systemevent__ import __systemevent__


class registerSystem(__systemevent__, __eventbinding__, __entitybinding__, __componentbinding__, __entityquery__, slashcommand):
    def __init__(self, majorVersion: int, minorVersion: int):
        self.__js__ = server.registerSystem(majorVersion, minorVersion)


# https://bedrock.dev/docs/stable/Scripting#log(Message)
def log(Message: str):
    server.client.log(Message)
