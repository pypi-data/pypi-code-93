import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Generator

from myvault.statics import Query


class Database:
    def __init__(self, db_path: Path):
        self.__conn = sqlite3.connect(database=db_path)
        self.__cur = self.__conn.cursor()
        self.__create_table()

    def __create_table(self):
        self.execute(Query.CREATE_TABLE.formatted())
        self.__commit()

    def insert_secret(self, folder: str, name: str, secret: str):
        time_now = self.get_current_datetime()
        self.execute(Query.INSERT_SECRET.formatted(folder=folder, name=name, secret=secret, timestamp=time_now))
        self.__commit()

    @staticmethod
    def get_current_datetime() -> datetime:
        return datetime.now()

    def execute(self, *args):
        self.__cur.execute(*args)

    def update_secret(self, folder: str, name: str, new_secret: str):
        time_now = self.get_current_datetime()
        self.execute(Query.UPDATE_SECRET.formatted(folder=folder, name=name, new_secret=new_secret, timestamp=time_now))
        self.__commit()

    def select_all(self) -> Generator:
        self.execute(Query.SELECT_ALL.formatted())
        for row in self.__cur:
            yield row

    def select_folder_and_names(self) -> Generator:
        self.execute(Query.SELECT_FOLDER_NAME.formatted())
        for row in self.__cur:
            yield row

    def select_secret(self, folder: str, name: str) -> str:
        self.execute(Query.SELECT_SECRET.formatted(folder=folder, name=name))
        selected_row = self.__cur.fetchone()
        return selected_row[0] if isinstance(selected_row, tuple) else None

    def delete_secret(self, folder: str, name: str):
        self.execute(Query.DELETE_SECRET.formatted(folder=folder, name=name))
        self.__commit()

    def execute_many(self, *args):
        self.__cur.executemany(*args)
        self.__commit()

    def __commit(self):
        self.__conn.commit()

    def close(self):
        self.__conn.close()
