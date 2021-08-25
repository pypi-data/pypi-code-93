"""


"""
import configparser
import os
import sqlite3


class Database:
    __colors = {
        "red": "\033[91m"
    }

    def __init__(self, iniSync: bool = False, canDelete: bool = False, messages: bool = True):
        """
        :param iniSync: Sync changes with the ini
        :param canDelete: Allow to delete columns/tables in your database automatically
        :param messages: optional messages as example "tables found that are not in the ini file"
        """
        self.ini = configparser.ConfigParser()
        self.iniSync = iniSync
        self.db: sqlite3.Connection = None
        self.fileName = "sqiniDatabase"
        self.filePath = "./"
        self.messages = messages
        self.canDelete = canDelete

    def read(self, path: str = ""):
        """
        Set your paths for the database, the Ini file must have the same name as the database

        :param path: enter here your path to your SQLite Database
        :return:
        """
        if path == "":
            if not self.fileName + ".db" in os.listdir(self.filePath):
                self.db = sqlite3.connect(self.filePath + self.fileName + ".db")
                open(self.filePath + self.fileName + ".ini", mode="w").close()
                self.ini.read(self.filePath + self.fileName + ".ini")
            else:
                print(self.__colors["red"], "path not specified, base database file already exist, please enter a path -> path=\"path_to_your_database\"")
        else:
            self.fileName = path.split("/")[-1].split(".", -1)[0]
            self.filePath = path.rsplit("/", 1)[0] + "/"
            try:
                if not self.fileName + ".db" in os.listdir(self.filePath):
                    self.db = sqlite3.connect(self.filePath + self.fileName + ".db")
                    if not self.fileName + ".ini" in os.listdir(self.filePath):
                        open(self.filePath + self.fileName + ".ini", mode="w").close()
                    self.ini.read(self.filePath + self.fileName + ".ini")
                else:
                    self.db = sqlite3.connect(self.filePath + self.fileName + ".db")
                    self.ini.read(self.filePath + self.fileName + ".ini")
            except NotADirectoryError:
                print(self.__colors["red"], f"invalid directory path, path not found \"{self.filePath}\". If the database in the same folder use \"./yourFile\"")

    def getTableInformations(self) -> dict:
        tables = {}
        raw = self.db.execute("SELECT name FROM sqlite_master WHERE type in ('table', 'view')").fetchall()
        autoIncrementTables = []
        if len(self.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'").fetchall()):
            for increment in self.db.executescript(f"SELECT * FROM sqlite_sequence").fetchall():
                autoIncrementTables.append(increment[0])
        for t in raw:
            table_name = t[0]
            if "sqlite_sequence" not in table_name:
                tables[table_name] = {
                    "columns": {},
                    "primarKeys": [],
                    "autoIncrement": []
                }
                tablecolumns = self.db.execute(f"PRAGMA table_info({table_name})").fetchall()
                indexList = self.db.execute(f"PRAGMA index_list({table_name})").fetchall()
                uniqueList = []
                for index in indexList:
                    uniqueList.append(self.db.execute(f"PRAGMA index_info({index[1]})").fetchone()[2])
                for c in tablecolumns:
                    autoIncrement = 0
                    unique = 0
                    if autoIncrementTables.__contains__(table_name): autoIncrement = 1
                    if uniqueList.__contains__(c[1]): unique = 1
                    tables[table_name]["columns"][c[0]] = {
                        "cid": c[0],
                        "name": c[1],
                        "type": c[2],
                        "notnull": c[3],
                        "dflt_value": c[4],
                        "pk": c[5],
                        "autoincerment": autoIncrement,
                        "unique": unique
                    }
        return tables

    def getTableInformation(self, table: str) -> dict:
        """
        Get information of a spefic table

        :param table:
        :return:
        """

        tables = self.getTableInformations()
        if tables.__contains__(table):
            return tables[table]
        else:
            raise ValueError(f'{table} not found')

    def syncToIni(self):
        """
        Generate the ini File with the Database Configs.
        In the base configuration is it disabled
        activate it with -> iniSync = True
        """
        if not self.iniSync:
            raise RuntimeError("ini sync function is disabled")
        tables = self.getTableInformations()
        for table in tables:
            if table not in self.ini.sections():
                self.ini.add_section(table)
            columnIniStr = "{} {} {} {} {} {}"
            columns = tables[table]["columns"]
            for c in columns:
                column = columns[c]
                dflt_value = 1
                if column["dflt_value"] is None: column["dflt_value"] = ""
                self.ini.set(table, column["name"],
                             columnIniStr.format(
                                 column["type"], column["notnull"], column["pk"],
                                 column["autoincerment"], column["unique"], column["dflt_value"]
                             ))

        self.save()

    def syncToDatabase(self):
        """
        Generate the database structure with the ini configuration.
        For delete unknown tables/columns activate it in the base configuration.
        -> canDelte = True
        """
        updateTables = {}
        tables = self.getTableInformations()
        selections = self.ini.sections()
        deleteTables = []
        for t in tables:
            if not selections.__contains__(t): deleteTables.append(t)
        if self.canDelete is not True:
            if len(deleteTables) > 0:
                deleteTables.clear()
                if self.messages: print("tables found that are not in the ini file")
        for x in selections:
            if self.canDelete is False:
                if x in tables.keys(): updateTables[x] = tables[x]; tables[x]["oldColumns"] = []
                else: updateTables[x] = {
                    "columns": {},
                    "primarKeys": [],
                    "autoIncrement": [],
                    "oldColumns": []
                }
            else:
                updateTables[x] = {
                    "columns": {},
                    "primarKeys": [],
                    "autoIncrement": [],
                    "oldColumns": []
                }
            if tables.__contains__(x):
                for cid in tables[x]["columns"]:
                    updateTables[x]["oldColumns"].append(tables[x]["columns"][cid]["name"])
            selectData = dict(self.ini.items(x))
            count = 0
            insertedKeys = []
            if self.canDelete is False:
                for key in updateTables[x]["columns"]:
                    insertedKeys.append(updateTables[x]["columns"][key]["name"])
            for key in selectData:
                if not insertedKeys.__contains__(key):
                    insertedKeys.append(key)
                    if self.canDelete:
                        insert: list = selectData[key].split(" ", 6)
                        if len(insert) < 6:
                            insert.append(None)
                        if isinstance(insert[5], str):
                            if insert[5].isnumeric():
                                insert[5] = int(insert[5])
                        updateTables[x]["columns"][count] = {
                            "cid": count,
                            "name": key,
                            "type": insert[0],
                            "notnull": int(insert[1]),
                            "dflt_value": insert[5],
                            "pk": int(insert[2]),
                            "autoincerment": int(insert[3]),
                            "unique": int(insert[4])
                        }
                        count += 1
                    else:
                        if len(updateTables[x]["columns"].keys()) > 0:
                            number = list(updateTables[x]["columns"].keys())[-1] + 1
                        else:
                            number = 0
                        insert = selectData[key].split(" ", 6)
                        if len(insert) < 6:
                            insert.append(None)
                        if isinstance(insert[5], str):
                            if insert[5].isnumeric():
                                insert[5] = int(insert[5])
                        updateTables[x]["columns"][number] = {
                            "cid": number,
                            "name": key,
                            "type": insert[0],
                            "notnull": int(insert[1]),
                            "dflt_value": insert[5],
                            "pk": int(insert[2]),
                            "autoincerment": int(insert[3]),
                            "unique": int(insert[4])
                        }
            for key in updateTables[x]["oldColumns"]:
                if not insertedKeys.__contains__(key):
                    updateTables[x]["oldColumns"].remove(key)
        for table in updateTables:
            sqlScript = ""
            if tables.__contains__(table):
                sqlScript += "" \
                            "BEGIN TRANSACTION;"
                sqlScript += f"ALTER TABLE {table} RENAME TO _{table}_old;"
            sqlScript += f"CREATE TABLE {table}("
            primaryKey = []
            allColumns = []
            for c in updateTables[table]["columns"]:
                column: dict = updateTables[table]["columns"][c]
                column_name = column["name"]; allColumns.append(column_name)
                column_type = column["type"]
                column_notnull = ""
                if column["notnull"] == 1: column_notnull = "NOT NULL"
                column_dflt_value = ""
                if column["dflt_value"] is not None: column_dflt_value = "DEFAULT " + str(column["dflt_value"])
                if not primaryKey.__contains__(True):
                    if column["autoincerment"] == 1:
                        primaryKey.clear()
                        primaryKey.append(True)
                        primaryKey.append(column_name)
                    else:
                        if column["pk"] == 1: primaryKey.append(column_name)
                column_unique = ""
                if column["unique"] == 1: column_unique = "UNIQUE"
                sqlScript += f'"{column_name}" {column_type} {column_notnull} {column_dflt_value} {column_unique},'

            if len(primaryKey) > 0:
                if primaryKey.__contains__(True):
                    primString = f'PRIMARY KEY("{primaryKey[1]}" AUTOINCREMENT)'
                else:
                    primString = 'PRIMARY KEY("' + '", "'.join(primaryKey) + '")'
                sqlScript += primString
            else:
                sqlScript = sqlScript[:-1]
            sqlScript += ");"
            if tables.__contains__(table):
                sqlScript += f"INSERT INTO {table}({', '.join(updateTables[table]['oldColumns'])}) SELECT {', '.join(updateTables[table]['oldColumns'])} FROM _{table}_old;"
                sqlScript += f"DROP TABLE _{table}_old;"
            # execute finish sql script
            self.db.executescript(sqlScript)
            self.db.commit()
        if self.canDelete:
            for table in deleteTables:
                self.db.execute(f"DROP TABLE {table}")
                self.db.commit()

    def deletecolumn(self, name: str):
        pass

    def save(self):
        with open(self.filePath + self.fileName + ".ini", mode="w") as iniFile:
            self.ini.write(iniFile)

    def tableUpdate(self, tabledict: dict, oldTableDict: dict):
        """
        :param tabledict:
        :param oldTableDict:
        :return:
        """

    def rename(self, table: str, current_column: str, new_name: str):
        """
        Rename a column in your sqlite database
        :param table: table name
        :param current_column: the current name of the column
        :param new_name: the new name of the column
        """
        pass

    def new_table(self, table: str):
        """
        create a table
        :param table: the name of the table
        """
        pass

    def add_column(self, tableName: str, columnName: str, columnType: str, notnull: bool = False, pk: bool = False, autoIncrement: bool = False, unique: bool = False, dflt_value: [int, str] = None):
        """
        Add a Column to a table with all possible settings.

        :param tableName: table name
        :param columnName: name of the column
        :param columnType: type of column
        :param notnull: if notnull
        :param pk: primary key
        :param autoIncrement: auto increment, only one per table
        :param unique: unique value
        :param dflt_value: default value
        :return:
        """
        tableInfo = self.getTableInformation(tableName)
        if len(tableInfo) == 0:
            if self.messages: return

        for x in tableInfo["columns"]:
            if tableInfo["columns"][x]["name"] == columnName:
                if self.messages: raise ValueError(f'{columnName} already used in {tableName}')
        new_cid = len(tableInfo["columns"])
        tableInfo["columns"][new_cid] = {
            "cid": new_cid,
            "name": columnName,
            "type": columnType,
            "notnull": notnull,
            "dflt_value": dflt_value,
            "pk": pk,
            "autoincerment": autoIncrement,
            "unique": unique
        }
        sqlStr = f"ALTER TABLE {tableName} ADD COLUMN "
        insert = ""
    def new_row(self, table: str, row: str):
        """
        :param table: table name
        :param row: Name of the row
        """
        pass


