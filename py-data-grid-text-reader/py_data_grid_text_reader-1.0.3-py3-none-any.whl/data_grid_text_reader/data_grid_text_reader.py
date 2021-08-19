# Copyright 2021 The Data Text Grid Reader Authors. All Rights Reserved.
# Portions Copyright 2019 The DataFrame Show Reader Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from typing import List

from sqlalchemy.engine.base import Connection

from data_grid_text_reader.text_util import strip_lines

DATA_TYPE_START_INDICATOR = '['
DATA_TYPE_END_INDICATOR = ']'


def parse_boolean(boolean: str):
    if boolean.lower() == 'true':
        return True
    elif boolean.lower() == 'false':
        return False
    else:
        raise ValueError(f'"{boolean}" is not a recognized boolean value')


def parse_date(date_text: str):
    """
    Convert a date string into a datetime instance that can be saved as an
    SQL DATE.
    :param date_text: A timestamp string in "YYYY-MM-DD" format
    :return: A datetime object
    """
    return datetime.strptime(date_text, '%Y-%m-%d')


def ts(timestamp: str):
    """
    Convert a timestamp string into a datetime instance that can be saved as an
    SQL TIMESTAMP.
    :param timestamp: A timestamp string in "YYYY-MM-DD HH:MM:SS" format
    :return: A datetime object
    """
    return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')


class DataGridTextReader:
    """
    Reads a string representing a database record set (that resembles the
    output of a call to the Apache Spark DataFrame.show() command) and converts
    it to a different representation, such as a list of dictionaries or a set
    of SQLCREATE TABLE and INSERT statements that can be used to persist the
    data to a database.

    The data grid text can take these forms:

    +--------+--------+
    |column_a|column_b|
    +--------+--------+
    |value 1a|value 1b|
    |value 2a|value 2b|
    +--------+--------+

    Optionally, row delimiters can be omitted, and comment lines and
    end-of-line comments can be present (whether or not row delimiters are
    provided):

    |column_a|column_b|
    |value 1a|value 1b|
    # This is a comment that gets ignored.
    |value 2a|value 2b| Another comment that gets ignored.

    Optionally, data types can be specified in a second header line, prefixed
    with the DATA_TYPE_START_INDICATOR ("["):
    +-------------+----------+------------+-------------------+-----------+
    |string_column|int_column|float_column|timestamp_column   |bool_column|
    [varchar      |int       |float       |timestamp          |boolean    ]
    +-------------+----------+------------+-------------------+-----------+
    |one          |1         |1.1         |2018-01-01 00:00:00|true       |
    |two          |2         |2.2         |2018-01-02 12:34:56|false      |
    +-------------+----------+------------+-------------------+-----------+
    """
    # By convention, the type map keys should be lowercase versions of SQL
    # keywords that would be valid in a CREATE TABLE statement.
    _TYPE_MAP = {
        'bigint': int,
        'boolean': parse_boolean,
        'date': parse_date,
        'double': float,
        'float': float,
        'int': int,
        'string': str,
        'timestamp': ts,
        'varchar': str,
    }

    def data_grid_text_to_sql(
            self,
            table_name: str,
            data_grid_text: str,
            default_data_type: str = 'varchar',
            overwrite: bool = True
    ) -> (str, str):
        """
        Takes a string representing a database record set and builds SQL
        CREATE TABLE and INSERT statements that can be used to persist the data
        to a database.
        :param table_name: The name of the table to be built
        :param data_grid_text: A string representing a record set. See the
               class comment for details on the expected string format.
        :param default_data_type: The default data type that will be used for all
               columns for which the data type is not specified in a data type
               declaration line
        :param overwrite: Specifies whether the resulting SQL statement should
               overwrite any existing table with the same name
        :return: A tuple of strings where the first string is the SQL CREATE TABLE
                 statement and the second string is the SQL INSERT statement
        """
        if not table_name:
            raise ValueError('table_name is required.')

        if not data_grid_text:
            raise ValueError('data_grid_text is required.')

        rows = []
        column_names = None
        types = None
        for line in data_grid_text.strip().splitlines():
            line = line.strip()
            if not line.startswith(tuple(f'|{DATA_TYPE_START_INDICATOR}')):
                continue
            line_parts = line.split('|')[1:-1]
            values = [part.strip() for part in line_parts]
            if column_names is None:
                column_names = values
                continue
            if line.startswith(DATA_TYPE_START_INDICATOR):
                if types is None:
                    line = line.replace(DATA_TYPE_START_INDICATOR, '|', 1) \
                               .rstrip(f'{DATA_TYPE_END_INDICATOR}|') + '|'
                    types = [part.strip() for part in line.split('|')[1:-1]]
                    types = [data_type if len(data_type) > 0 else default_data_type
                             for data_type in types]
                    continue
                else:
                    raise ValueError('Cannot have more than one data type declaration line.')

            if types is None:
                types = [default_data_type] * len(column_names)

            self._cast_types(values, types)
            for i, value in enumerate(values):
                if type(value) in [str, datetime]:
                    value = f"'{value}'"
                elif isinstance(value, bool):
                    value = str(value).upper()
                elif value is None:
                    value = 'NULL'
                else:
                    value = str(value)
                values[i] = value
            rows.append(f"({', '.join(values)})")

        if types is None:
            # This can happen if data types are not specified and no data rows are
            # provided.
            types = [default_data_type] * len(column_names)

        column_definitions = [f'{column_name} {types[i]}' for
                              i, column_name in enumerate(column_names)]
        column_definitions = ',\n'.join(column_definitions)
        create_or_replace_statement = 'CREATE OR REPLACE' if overwrite else 'CREATE'
        create_table_statement = strip_lines(
            f"{create_or_replace_statement} TABLE {table_name}(\n{column_definitions}\n);")

        if rows:
            insert_statement = strip_lines(
                f"INSERT INTO {table_name}\n({', '.join(column_names)}) VALUES\n" +
                ',\n'.join(rows) + ';')
        else:
            insert_statement = None

        return create_table_statement, insert_statement

    def data_grid_text_to_list(
            self,
            data_grid_text: str,
            default_data_type: str = 'varchar'
    ) -> List[dict]:
        """
        Takes a string representing a database record set and builds a Python
        list of dicts representing the record set.
        :param data_grid_text: A string representing a record set. See the
               class comment for details on the expected string format.
        :param default_data_type: The default data type that will be used for all
               columns for which the data type is not specified in a data type
               declaration line
        :return: A list of dicts representing the record set
        """
        if not data_grid_text:
            raise ValueError('data_grid_text is required.')

        result = []
        column_names = None
        types = None
        for line in data_grid_text.strip().splitlines():
            line = line.strip()
            if not line.startswith(tuple(f'|{DATA_TYPE_START_INDICATOR}')):
                continue
            line_parts = line.split('|')[1:-1]
            values = [part.strip() for part in line_parts]
            if column_names is None:
                column_names = values
                continue
            if line.startswith(DATA_TYPE_START_INDICATOR):
                if types is None:
                    line = line.replace(DATA_TYPE_START_INDICATOR, '|', 1) \
                               .rstrip(f'{DATA_TYPE_END_INDICATOR}|') + '|'
                    types = [part.strip() for part in line.split('|')[1:-1]]
                    types = [data_type if len(data_type) > 0 else default_data_type
                             for data_type in types]
                    continue
                else:
                    raise ValueError('Cannot have more than one data type declaration line.')

            if types is None:
                types = [default_data_type] * len(column_names)

            self._cast_types(values, types)
            row = {}
            for i, value in enumerate(values):
                row[column_names[i]] = value
            result.append(row)
        return result

    def save_as_table(
            self,
            table_name: str,
            data_grid_text: str,
            connection: Connection,
            default_data_type: str = 'varchar',
            overwrite: bool = False
    ) -> None:
        """
        Takes a string representing a database record set and persists it to a
        new database table.
        :param table_name: The name of the table to be persisted.
               Can be in "<schema_name>.<table_name>" format
               (e.g., "my_schema.my_table"), or simply in "<table_name>"
               format to be saved to the default schema.
        :param data_grid_text: A string representing a record set. See the
               class comment for details on the expected string format.
        :param connection: A SQLAlchemy database Connection instance
        :param default_data_type: The default data type that will be used for all
               columns for which the data type is not specified in a data type
               declaration line
        :param overwrite: If true, any pre-existing table will be overwritten.
               If false and the specified table already exists, an error will be
               thrown.
        :return: None
        """
        if not connection:
            raise ValueError('connection is required.')
        create_table_sql, insert_sql = self.data_grid_text_to_sql(
            table_name, data_grid_text, default_data_type, overwrite)
        connection.execute(create_table_sql)
        if insert_sql:
            connection.execute(insert_sql)

    @classmethod
    def _cast_types(cls, values: list, types: list):
        for i, value in enumerate(values):
            values[i] = (None if value and value.lower() == 'null'
                         else cls._get_cast_function(types[i])(value))

    @classmethod
    def _get_cast_function(cls, data_type: str) -> type:
        data_type_lower = data_type.lower()
        if data_type_lower not in cls._TYPE_MAP:
            raise ValueError(f'Unrecognized data type "{data_type}"')
        return cls._TYPE_MAP[data_type_lower]
