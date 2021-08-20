import logging
import os
import sqlite3
import time
from time import strftime
from typing import List

import pandas as pd

from notetool.tool import log

logging.basicConfig(format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s')


class BaseTable:
    def __init__(self, table_name='default_table', columns=None):
        self.table_name = table_name
        self.columns = columns
        self.logger = log(table_name)

    def execute(self, sql):
        raise Exception("还没有实现")

    def insert(self, properties: dict):
        properties = self.encode(properties)
        keys, values = self._properties2kv(properties)

        sql = """insert or ignore into {} ({}) values ({})""".format(self.table_name, ', '.join(keys),
                                                                     ', '.join(values))
        return self.execute(sql)

    def update(self, properties: dict, condition: dict):
        properties = self.encode(properties)
        equal = self._properties2equal(properties)
        equal2 = self._properties2equal(condition)
        sql = """update  {} set {} where {}""".format(self.table_name, ', '.join(equal), ' and '.join(equal2))
        return self.execute(sql)

    def decode(self, properties: dict):
        return properties

    def encode(self, properties: dict):
        return properties

    def count(self, properties: dict):
        properties = properties or {}
        values = []
        for key in self.columns:
            value = str(properties.get(key, ''))
            if len(value) > 0 and len(key) > 0:
                values.append("{}='{}'".format(key, value))

        sql = """select count(1) from {} where {}""".format(self.table_name, ' and '.join(values))

        rows = self.execute(sql)
        for row in rows:
            return row[0]
        return 0

    def select_all(self):
        return self.select("select * from table_name")

    def select(self, sql):
        sql = self.sql_format(sql)

        rows = self.execute(sql)
        return [] if rows is None else [row for row in rows]

    def _properties2kv(self, properties: dict):
        if self.columns is None:
            raise Exception("origin_keys cannot be None")
        keys = []
        values = []
        for key in self.columns:
            value = str(properties.get(key, '')).replace("'", '')
            if len(key) > 0 and len(value) > 0:
                keys.append(key)
                values.append("'{}'".format(value))
        return keys, values

    def _properties2equal(self, properties: dict):
        if self.columns is None:
            raise Exception("origin_keys cannot be None")
        equals = []
        for key in self.columns:
            value = properties.get(key, None)
            if len(key) > 0 and value is not None:
                if isinstance(value, str):
                    equals.append("{}='{}'".format(key, value))
                else:
                    equals.append("{}={}".format(key, value))
        return equals

    def sql_format(self, sql):
        sql = sql.replace('table_name', self.table_name)
        return sql


class SqliteTable(BaseTable):
    def __init__(self, db_path, *args, **kwargs):
        super(SqliteTable, self).__init__(*args, **kwargs)
        self.db_path = db_path
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def execute(self, sql):
        try:
            rows = self.cursor.execute(sql)
            self.conn.commit()
            return rows
        except Exception as e:
            print("{}  with error:{}".format(sql, e))
            return

    def execute_without_commit(self, sql):
        try:
            rows = self.cursor.execute(sql)
            return rows
        except Exception as e:
            print("{}  with error:{}".format(sql, e))
            return

    def close(self):
        self.cursor.close()
        self.conn.close()

    def select_pd(self, sql="select * from table_name"):
        sql = self.sql_format(sql)
        return pd.read_sql(sql, self.conn)

    def save_and_truncate(self):
        result = pd.read_sql("select * from {}".format(self.table_name), self.conn)

        count = len(result)
        path = ('{}/{}-{}-{}'.format(os.path.dirname(self.db_path), self.table_name, count,
                                     strftime("%Y%m%d#%H:%M:%S", time.localtime())))
        result.to_csv(path)
        self.logger.info("save to csv:{}->{}".format(count, path))

        self.execute("delete from {}".format(self.table_name))
        self.logger.info("delete from {}".format(self.table_name))
        self.execute("VACUUM")
        self.logger.info("VACUUM")
        return result

    def vacuum(self):
        self.execute("VACUUM")

    def insert_list(self, property_list: List[dict]):
        values = [tuple([properties.get(key, '') for key in self.columns]) for properties in property_list]
        sql = "insert or ignore into {} values ({})".format(self.table_name, ','.join(['?'] * len(self.columns)))

        self.cursor.executemany(sql, values)
        self.conn.commit()
        return True
