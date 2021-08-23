from __future__ import annotations

import typing as t

import datetime as dt
from decimal import Decimal


class SQLType:

    db_type: str
    py_type: type


class AUTO(SQLType):
    db_type = 'INTEGER'
    py_type = int


class BIGAUTO(SQLType):
    db_type = 'BIGINT'
    py_type = int


class BIGINT(SQLType):
    db_type = 'BIGINT'
    py_type = int


class BLOB(SQLType):
    db_type = 'BLOB'
    py_type = bytes


class BOOL(SQLType):
    db_type = 'SMALLINT'
    py_type = int


class CHAR(SQLType):
    db_type = 'CHAR'
    py_type = str


class DATE(SQLType):
    db_type = 'DATE'
    py_type = dt.date


class DATETIME(SQLType):
    db_type = 'DATETIME'
    py_type = dt.datetime


class DECIMAL(SQLType):
    db_type = 'DECIMAL'
    py_type = Decimal


class DOUBLE(SQLType):
    db_type = 'REAL'
    py_type = float


class FLOAT(SQLType):
    db_type = 'REAL'
    py_type = float


class INT(SQLType):
    db_type = 'INTEGER'
    py_type = int


class SMALLINT(SQLType):
    db_type = 'SMALLINT'
    py_type = int


class TEXT(SQLType):
    db_type = 'TEXT'
    py_type = str


class TIME(SQLType):
    db_type = 'TIME'
    py_type = dt.time


class UUID(SQLType):
    db_type = 'TEXT'
    py_type = str


class UUIDB(SQLType):
    db_type = 'BLOB'
    py_type = bytes


class VARCHAR(SQLType):
    db_type = 'VARCHAR'
    py_type = str


MAP_PYTYPES = {
    int: INT,
    str: t.Annotated[VARCHAR, 256],
    bool: BOOL,
    float: FLOAT,
    dt.date: DATE,
    dt.time: TIME,
    dt.datetime: DATETIME,
    bytes: BLOB,
}
