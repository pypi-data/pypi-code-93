import os
# from common.singleton import singleton
from infrastructure.singleton import singleton

class ConfigKeys:
    ENABLE_THEME = "EnableTheme"
    LOGIN_USER = "User"
    LOGIN_PASSWORD = "Password"

@singleton
class ConfigHelper:
    
    __config = dict()

    def __init__(self):
        #Ruta absoluta
        configPath = os.path.abspath("../config.ini")
        if not os.path.isfile(configPath):
            configPath=os.path.abspath("./section22-TkinterMySql/config.ini")


        f = open(configPath,"r")

        lines = f.readlines()
        for line in lines:
            if(not line.startswith("#")):
                key,value = line.strip('\n\r\t').split("=")
                self.__config.setdefault(key,value)

        f.close()

    @classmethod
    def GetConfig(cls):
        return cls.__config

    @classmethod
    def GetValue(cls, key):
        return cls.__config.get(key)

