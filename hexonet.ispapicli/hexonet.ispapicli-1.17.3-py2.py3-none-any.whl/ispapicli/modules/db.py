import os
import re
import sys
import json
from tinydb import TinyDB, Query


class DB:
    def __init__(self) -> None:
        self.__initAppDirectories()
        self.initDB()
        self.commandsTable = "commands"
        self.loginTable = "login"
        self.subUserTable = "subuser"

    def initDB(self):
        """
        Init DB dirs

        Returns:
        --------
        Null
        """
        # check for first use of the tool
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
            f = open(self.db_file_path, "w")
            f.close()

        self.db = TinyDB(self.db_file_path)
        self.query = Query()

    def __initAppDirectories(self):
        """
        Checks whether the app is running from the editor or from an executable file

        Returns:
        --------
        Null
        """
        if getattr(sys, "frozen", False):
            self.absolute_dirpath = os.path.dirname(sys.executable)
            self.db_path = os.path.join(self.absolute_dirpath, "db")
            self.db_file_path = os.path.join(self.absolute_dirpath, "db/db.json")
        elif __file__:
            self.absolute_dirpath = os.path.dirname(__file__)
            self.db_path = os.path.join(self.absolute_dirpath, "../db/")
            self.db_file_path = os.path.join(self.absolute_dirpath, "../db/db.json")

    def getAllCommands(self):
        """
        Retrieves all commands from DB

        Returns:
        --------
        List: data
        """
        data = []
        try:
            table = self.db.table(self.commandsTable)
            data = table.all()
            return data
        except:
            return data

    def getCommand(self, command_name):
        """
        Retrieves a single command from DB

        Returns:
        --------
        List: data
        """
        data = []
        try:
            table = self.db.table(self.commandsTable)
            data = table.search(
                self.query.command.matches(command_name, flags=re.IGNORECASE)
            )
            return data
        except:
            return data

    def getLoginInfo(self):
        """
        Retrieves login info from DB

        Returns:
        --------
        List: data
        """
        data = []
        try:
            loginTable = self.db.table(self.loginTable)
            data = loginTable.all()
            return data
        except:
            return data

    def setLoginInfo(self, data):
        """
        Saves login info to DB

        Returns:
        --------
        Bool: True || False
        """
        try:
            # delete old session
            self.db.drop_table("login")
            # add new session
            table = self.db.table(self.loginTable)
            table.insert(data)
            return True
        except:
            return False

    def deleteLoginInfo(self):
        """
        Deletes login info from DB

        Returns:
        --------
        Bool: True || False
        """
        try:
            self.db.drop_table(self.loginTable)
            return True
        except:
            return False

    def insertCommand(self, commandName, data):
        """
        Inserts or updates a command if exist

        Returns:
        --------
        Bool: True || False
        """
        try:
            table = self.db.table(self.commandsTable)
            # insert and update where necessary
            result = table.upsert(data, self.query["command"] == commandName)
            print("Command saved: ", commandName)
            return True
        except Exception as e:
            print(e)
            return False

    def insertSubuser(self, subuser, data):
        """
        Inserts or udpates a subuser if exist

        Returns:
        --------
        Bool: True || False
        """
        try:
            table = self.db.table(self.subUserTable)
            result = table.upsert(data, self.query["subuser"] == subuser)
            print("subuser save: ", subuser)
            return True
        except Exception as e:
            print(e)
            return False

    def getAllSubusers(self):
        """
        Retrieves all commands from DB

        Returns:
        --------
        List: data
        """
        data = []
        try:
            table = self.db.table(self.subUserTable)
            data = table.all()
            return data
        except:
            return data

    def checkCommandExist(self, table, command):
        """
        Checks a command if exist

        Returns:
        --------
        Bool: False || List: result
        """
        try:
            result = table.search(self.query["command"] == command)
            return result
        except:
            return False

    def __compareCommandData(self, d1, d2):
        """
        Compares two ditcs

        Returns:
        --------
        Bool: True | False
        """
        try:
            for k in d1:
                if k not in d2:
                    return False
                else:
                    if type(d1[k]) is dict:
                        self.__compareCommandData(d1[k], d2[k])
                    else:
                        if d1[k] != d2[k]:
                            return False
        except Exception as e:
            print(e)
            return False
        return True
