import sqlite3
from sqlite3 import Connection


def sql_connect(path: str, **kwargs) -> Connection:
    return sqlite3.connect(path, **kwargs)
