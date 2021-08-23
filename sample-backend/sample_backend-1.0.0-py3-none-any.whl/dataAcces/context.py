# import mysql.connector
import sqlite3
import os

class Context:

    #SQLITE
    def __init__(self) -> None:
        
        #Ruta absoluta
        databasePath = os.path.abspath("./sample.db")
        if not os.path.isfile(databasePath):
            databasePath=os.path.abspath("../../database/sample.db")

        self.__db = sqlite3.connect(databasePath)
        self.db = self.__db

        self.__cursor = self.__db.cursor()
        self.Cursor = self.__cursor

    def CreateConnection(self):
        return [self.__db, self.__cursor]

    # #MYSQL
    # def __init__(self) -> None:
    #     self.__db = mysql.connector.connect(
    #         host= "localhost",
    #         user = "root",
    #         passwd = "sql.123",
    #         port = 3306,
    #         database = "test"
    #     )
    #     self.db = self.__db

    #     self.__cursor = self.__db.cursor(buffered=True)
    #     self.Cursor = self.__cursor

    # def CreateConnection(self):
    #     return [self.__db, self.__cursor]