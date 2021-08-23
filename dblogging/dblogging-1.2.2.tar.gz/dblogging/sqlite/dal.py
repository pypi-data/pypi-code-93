import sqlite3
import os
import sys

SQL_SCHEMA = """
-- pragma
pragma foreign_keys = on;
pragma journal_mode = wal;

-- Legend
create table if not exists log_tags (
    name text not null primary key,
    value integer not null,
    color text not null
);

-- Log Entries
create table if not exists log_entries (
    id integer primary key autoincrement,
    file_path text not null,
    function_name text,
    line_num integer not null,
    msg text not null,
    tag_name text not null,
    depth integer not null,
    thread_id integer,
    thread_name text,
    is_main_thread int not null,
    timestamp datetime default (datetime('now', 'localtime'))
);
"""

class Table:
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    @staticmethod
    def _insert_query(table, data: dict):
        return "insert into {table} ({rows}) values ({values})".format(
            table=table,
            rows=','.join(data.keys()),
            values=','.join(['?' for _ in range(len(data))])
        ), tuple(data.values())


class LogTags(Table):
    table_name = 'log_tags'

    name = 'name'
    value = 'value'
    color = 'color'

    def __init__(self, cursor: sqlite3.Cursor):
        super().__init__(cursor=cursor)

    def insert(self, name: str, value: int, color: str):
        data = {
            self.name : name,
            self.value: value,
            self.color: color
        }

        query = self._insert_query(table=self.table_name, data=data)
        self._cursor.execute(*query)


class LogEntries(Table):
    table_name = 'log_entries'

    id = 'id'
    file_path = 'file_path'
    function_name = 'function_name'
    line_num = 'line_num'
    msg = 'msg'
    tag_name = 'tag_name'
    depth = 'depth'
    thread_id = 'thread_id'
    thread_name = 'thread_name'
    is_main_thread = 'is_main_thread'
    timestamp = 'timestamp'

    def __init__(self, cursor: sqlite3.Cursor):
        super().__init__(cursor=cursor)

    def insert(self, file_path: str, function_name: str, line_num: int, msg: str, tag_name: str, depth: int,
               thread_id: int, thread_name: str, is_main_thread: bool):
        data = {
            self.file_path     : file_path,
            self.function_name : function_name,
            self.line_num      : line_num,
            self.msg           : msg,
            self.tag_name      : tag_name,
            self.depth         : depth,
            self.thread_id     : thread_id,
            self.thread_name   : thread_name,
            self.is_main_thread: int(is_main_thread)
        }

        query = self._insert_query(table=self.table_name, data=data)
        self._cursor.execute(*query)


class LoggerSql:
    def __init__(self, db_file_name: str):
        _sql = sqlite3.connect(str(db_file_name), uri=True, isolation_level=None, check_same_thread=False)
        self._cursor = _sql.cursor()
        self.log_tags = LogTags(cursor=self._cursor)
        self.log_entries = LogEntries(cursor=self._cursor)

    def create_database(self):
        self._cursor.executescript(SQL_SCHEMA)

    def select(self, query: str, parameters: tuple = tuple()):
        results = self._cursor.execute(query, parameters).fetchall()
        description = self._cursor.description
        return SelectResult(
            columns=[desc[0] for desc in description],
            rows=results
        )


class SelectResult:
    def __init__(self, columns: list, rows: list):
        self.columns = columns
        self.rows = rows

    @property
    def dict(self):
        return dict(zip(self.columns, *self.rows))

    def iterate(self):
        for i in range(len(self.rows)):
            yield dict(zip(self.columns, self.rows[i]))
