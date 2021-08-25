# -*- coding: utf-8 -*-

# Microlib is a small collection of useful tools.
# Copyright 2020 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Microlib.

# Microlib is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Microlib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Microlib; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sqlite3

from intspan import intspan

from microlib import terminal


def intspan2sqllist(s):
    """Turn an ints' span (given as str) to a SQLite list of values."""
    values = ', '.join([str(n) for n in list(intspan(s))])
    return f'({values})'


# Inspiration from: https://gist.github.com/miku/6522074
class ContextManager:
    """
    Simple Context Manager for sqlite3 databases.

    Regular usage makes it commit AND close everything at exit.

    Setting testing to True makes the Manager cancel any modification at exit,
    instead of committing. It is then intended to be used as a mock in test
    suites, like:

    def test_my_stuff(mocker):
        mocker.patch('microlib.database.ContextManager',
                     return_value=ContextManager(TESTDB_PATH, testing=True))

    or this way:

    def test_my_stuff():
        with ContextManager(TESTDB_PATH, testing=True) as cursor:
            # and, for instance:
            db = Operator(cursor)
    """
    def __init__(self, path, testing=False):
        self.path = path
        self.conn = None
        self.cursor = None
        self.testing = testing

    def __enter__(self):
        self.conn = sqlite3.connect(str(self.path))
        self.cursor = self.conn.cursor()
        if self.testing:
            self.cursor.execute('SAVEPOINT starttest;')
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        if self.testing:
            self.conn.execute('ROLLBACK TO SAVEPOINT starttest;')
        else:
            self.conn.commit()
        self.conn.close()


class Operator:
    """
    A collection of shortcuts to execute commands on a sqlite3 db.

    It can be used in conjunction with the ContextManager, for instance:

    with microlib.database.Manager(PATH_TO_DB) as cursor:
        mydb = microlib.database.Operator(cursor)

    """
    def __init__(self, cursor):
        self.cursor = cursor

    def list_tables(self):
        """List all available tables."""
        results = self.cursor.execute(
            'SELECT name FROM sqlite_master WHERE type=\'table\';')
        return [_[0] for _ in results.fetchall()]

    def table_exists(self, name):
        """True if a table of this name does exist in the database."""
        return name in self.list_tables()

    def _assert_table_exists(self, name):
        """Raise an exception the database contains no table named 'name'."""
        if not self.table_exists(name):
            raise ValueError(f'In database, cannot find a table named '
                             f'"{name}"')
        return True

    def _assert_row_exists(self, table_name, id_):
        """Raise an exception if no such row in the table exists."""
        cmd = f'SELECT EXISTS(SELECT 1 FROM {table_name} WHERE id={id_});'
        row_exists = self.cursor.execute(cmd).fetchall()[0][0]
        if not row_exists:
            raise ValueError(f'In database, cannot find a row number '
                             f'{id_} in table "{table_name}"')
        return True

    def _exec(self, table_name, cmd, id_=None):
        """
        Safe execution of the sql command on existing tables: start by checking
        table exists, then possibly the row id_ too, and finally execute the
        command. If table_name is provided as None, then no check is run, the
        command is simply directly executed.
        """
        if table_name is not None:
            self._assert_table_exists(table_name)
            if id_ is not None:
                self._assert_row_exists(table_name, id_)
        return self.cursor.execute(cmd)

    def rename_table(self, name, new_name):
        """Change a table's name."""
        self._exec(name, f'ALTER TABLE `{name}` RENAME TO `{new_name}`;')

    def update_table(self, name, id_, content):
        """Update content of row number 'id_' in table 'name'."""
        col_titles = self.get_cols(name)
        self._assert_row_exists(name, id_)
        if len(content) != len(col_titles):
            raise ValueError(f'In database, {content} requires {len(content)} '
                             f'columns, but table {name} has only '
                             f'{len(col_titles)} columns.')
        pairs = zip(col_titles, content)
        col_values = ', '.join(f'{p[0]}="{p[1]}"' for p in pairs)
        self._exec(name, f'UPDATE {name} SET {col_values} WHERE id={id_};')

    def copy_table(self, name1, name2, sort=False):
        """Copy table name1 as name2."""
        if self.table_exists(name2):
            raise ValueError(f'In database, action cancelled: a table named '
                             f'"{name2}" already exists. Please rename or '
                             f'remove it before using this name.')
        orderby = ''
        if sort:
            if sort not in [n + 1 for n in range(len(self.get_cols(name1)))]:
                raise ValueError(f'In database, cannot find a column number '
                                 f'{sort} in table "{name1}"')
            orderby = f' ORDER BY ' \
                f'{self.get_cols(name1, include_id=True)[sort]}'
        self.create_table(name2, self.get_cols(name1))
        titles = ', '.join(self.get_cols(name1))
        cmd = f'INSERT INTO {name2} ({titles}) '\
            f'SELECT {titles} FROM {name1}{orderby};'
        self._exec(None, cmd)

    def _original_name(self, name):
        """Create a table name that does not already exists in the database."""
        i = 0
        new_name = name
        while self.table_exists(new_name):
            new_name = name + f'_{i}'
            i += 1
        return new_name

    def sort_table(self, name, n):
        """Sort table "name" using column number n"""
        temp_name = self._original_name(name)
        self.copy_table(name, temp_name, sort=n)
        self.remove_table(name)
        self.rename_table(temp_name, name)

    def get_cols(self, table_name, include_id=False):
        """List all columns of a given table."""
        cursor = self._exec(table_name, f'SELECT * from {table_name};')
        start = 0 if include_id else 1
        return [_[0] for _ in cursor.description][start:]

    def get_rows_nb(self, table_name):
        """Return rows' number of a given table."""
        cmd = f'SELECT COUNT(*) FROM {table_name};'
        return tuple(self._exec(table_name, cmd))[0][0]

    def get_rows(self, cols, table_name, where_clause):
        """Return selected columns whose values match the where_clause."""
        cols = ','.join(cols)
        cmd = f'SELECT {cols} FROM {table_name} WHERE {where_clause};'
        return self._exec(table_name, cmd).fetchall()

    def get_table(self, name, include_headers=False, sort=False):
        """Return a list of all table's lines."""
        headers = []
        cols = ','.join(self.get_cols(name, include_id=True))
        content = self._exec(name, f'SELECT {cols} FROM {name};').fetchall()
        content = [(str(t[0]), ) + t[1:] for t in content]
        if sort:
            if sort not in [n for n in range(len(content[0]))]:
                raise ValueError(f'In database, cannot find a column number '
                                 f'{sort} in table "{name}"')
            content = sorted(content, key=lambda row: row[sort])
        if include_headers:
            headers = [tuple(self.get_cols(name, include_id=True))]
        return headers + content

    def table_to_text(self, name):
        """Return table's content as text in a tabular."""
        content = self.get_table(name, include_headers=True)
        return terminal.tabulate(content)

    def remove_table(self, name):
        """Remove table name."""
        self._exec(name, f'DROP TABLE {name};')

    def _create_cmd(self, name, col_titles):
        titles = ' TEXT, '.join(col_titles) + ' TEXT'
        return f'CREATE TABLE {name} (id INTEGER PRIMARY KEY, {titles});'

    def create_table(self, name, col_titles, content=None):
        """Create table name using given col_titles and content."""
        cmd = self._create_cmd(name, col_titles)
        self._exec(None, cmd)
        if content is not None:
            self.insert_rows(name, content, col_titles=col_titles)

    def _titles_and_qmarks(self, col_titles):
        titles = ', '.join(list(col_titles))
        qmarks = '?, ' * (len(col_titles) - 1) + '?'
        return (titles, qmarks)

    def _content(self, rows):
        return rows

    def insert_rows(self, table_name, rows, col_titles=None):
        """Insert rows to the table."""
        if col_titles is None:
            col_titles = self.get_cols(table_name)
        for row in rows:
            if len(col_titles) != len(row):
                data = [f"'{item}'" for item in row]
                data = ', '.join(data)
                raise ValueError(f'In database, {data} requires {len(row)} '
                                 f'columns, but table {table_name} has only '
                                 f'{len(col_titles)} columns.')
        titles, qmarks = self._titles_and_qmarks(col_titles)
        cmd = f'INSERT INTO {table_name}({titles}) VALUES({qmarks})'
        content = self._content(rows)
        self.cursor.executemany(cmd, content)

    def merge_tables(self, name1, name2):
        """Insert rows of table name1 table into name2."""
        if len(self.get_cols(name1)) != len(self.get_cols(name2)):
            raise ValueError(f'In database, cannot merge table {name1} into '
                             f'table {name2} because they have different '
                             f'numbers of columns ({self.get_cols(name1)} and '
                             f'{self.get_cols(name2)}).')
        titles1 = ', '.join(self.get_cols(name1))
        titles2 = ', '.join(self.get_cols(name2))
        self._exec(None, f'INSERT INTO {name2} ({titles2}) '
                   f'SELECT {titles1} FROM {name1};')

    def _reset_table_ids(self, name):
        """Reset the ids of a table to remove gaps created by rows removals."""
        temp_name = self._original_name(name)
        self.copy_table(name, temp_name)
        self.remove_table(name)
        self.rename_table(temp_name, name)

    def remove_row(self, table_name, id_):
        """Remove row matching id_ in the table."""
        cmd = f'DELETE FROM {table_name} WHERE id = {id_};'
        self._exec(table_name, cmd, id_=id_)
        self._reset_table_ids(table_name)

    def remove_rows(self, table_name, id_span):
        """Remove rows matching the ids from id_span from the table."""
        self._assert_table_exists(table_name)
        for id_ in list(intspan(id_span)):
            self._assert_row_exists(table_name, id_)
        values = intspan2sqllist(id_span)
        cmd = f'DELETE FROM {table_name} WHERE id IN {values};'
        self._exec(table_name, cmd)
        self._reset_table_ids(table_name)


class Ts_Operator(Operator):
    """
    Add "hidden" "timestamp" column to the tables, plus related features.

    The timestamp column will not show up in the get_cols() results.
    Extra features include:
    - it's possible to timestamp any row
    - it's possible to reset the timestamp of the most oldest timestamped rows
    - it's possible to randomly draw several rows
    """

    def get_cols(self, table_name, include_id=False):
        return super().get_cols(table_name, include_id=include_id)[:-1]

    def _create_cmd(self, name, col_titles):
        titles = ' TEXT, '.join(col_titles) + ' TEXT, '
        return f'CREATE TABLE {name} (id INTEGER PRIMARY KEY, '\
            f'{titles}timestamp INTEGER);'

    def _titles_and_qmarks(self, col_titles):
        titles = ', '.join(list(col_titles) + ['timestamp'])
        qmarks = '?, ' * len(col_titles) + '?'
        return (titles, qmarks)

    def _content(self, rows):
        return [item + (0, ) for item in rows]

    def _timestamp(self, table_name, id_):
        """Set timestamp to entry matching id_ in the table."""
        cmd = f"""UPDATE {table_name} SET timestamp = strftime('%Y-%m-%d %H:%M:%f')
    WHERE id = {id_};"""
        self._exec(table_name, cmd, id_=id_)

    def _reset(self, table_name, n):
        """Reset the n oldest timestamped entries."""
        cmd = f"""UPDATE {table_name} SET timestamp=0
    WHERE id IN (SELECT id FROM {table_name} WHERE timestamp != 0
    ORDER BY timestamp LIMIT {n});"""
        self._exec(table_name, cmd)

    def _full_reset(self, table_name):
        """Reset all entries."""
        self._reset(table_name, self.get_rows_nb(table_name))

    def draw_rows(self, table_name, n, oldest_prevail=False):
        """Return n rows, randomly chosen."""
        rows_nb = self.get_rows_nb(table_name)
        if n > rows_nb:
            raise ValueError(f'{n} rows are required from "{table_name}", '
                             f'but it only contains {rows_nb} rows.')
        timestamps_clause = ''
        if oldest_prevail:  # If timestamps must be taken into account
            cmd = f'SELECT COUNT(*) FROM {table_name} WHERE timestamp=0;'
            free_nb = tuple(self._exec(table_name, cmd))[0][0]
            if n > free_nb:
                self._reset(table_name, n - free_nb)
            timestamps_clause = 'WHERE timestamp=0 '
        cols_list = ','.join(self.get_cols(table_name))
        cmd = f'SELECT {cols_list} FROM {table_name} {timestamps_clause}'\
            f'ORDER BY random() LIMIT {n};'
        rows = self._exec(table_name, cmd).fetchall()
        return rows
