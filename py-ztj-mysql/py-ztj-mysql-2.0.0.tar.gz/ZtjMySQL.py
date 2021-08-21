# -*- coding: utf-8 -*-
# Author: Ztj
# Email: ztj1993@gmail.com

import pymysql
from dbutils.pooled_db import PooledDB
from pymysql.connections import Connection
from pymysql.cursors import DictCursor


class MySQL(object):

    def __init__(self, **kwargs):
        self._pool = None
        self._connection = None
        self.options = kwargs

    def pool(self) -> PooledDB:
        if self._pool is None:
            self._pool = PooledDB(creator=pymysql, cursorclass=DictCursor, **self.options)
        return self._pool

    def destroy(self):
        self._pool = None
        self._connection = None

    def reconnection(self) -> Connection:
        return self.pool().connection()

    def connection(self) -> Connection:
        if self._connection is None:
            self._connection = self.reconnection()
        return self._connection

    def ping(self) -> bool:
        try:
            self.connection().ping()
            return True
        except:
            return False

    def exec_sql(self, sql):
        connection = self.connection()
        with connection.cursor() as cursor:
            if isinstance(sql, str):
                cursor.execute(sql)
            else:
                cursor.execute(*sql)
            connection.commit()

    def exec_sql_list(self, sql_list):
        connection = self.connection()
        with connection.cursor() as cursor:
            for sql in sql_list:
                if isinstance(sql, str):
                    cursor.execute(sql)
                else:
                    cursor.execute(*sql)
            connection.commit()

    def get_record(self, sql, callback, *args, **kwargs):
        connection = self.connection()
        with connection.cursor() as cursor:
            if isinstance(sql, str):
                cursor.execute(sql)
            else:
                cursor.execute(*sql)
            result = callback(cursor, *args, **kwargs)
        return result

    @staticmethod
    def record_callback_fetch_all(cursor: DictCursor):
        return cursor.fetchall()

    @staticmethod
    def record_callback_fetch_one(cursor: DictCursor):
        return cursor.fetchone()

    @staticmethod
    def record_callback_fetch_value(cursor: DictCursor, field=None):
        row = cursor.fetchone()
        return list(row.values())[0] if field is None else row.get(field)
