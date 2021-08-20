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

import json
from datetime import datetime

from pytest import fixture, raises
from sqlalchemy.engine.base import Connection

from data_grid_text_reader.assert_equal_lists import assert_equal
from data_grid_text_reader.data_grid_text_reader import DataGridTextReader
from tests.database_test_base import DatabaseTestBase


class DataGridTextReaderTestBase(DatabaseTestBase):
    """
    Contains test methods that can be run against different databases by
    creating subclasses that provide different values for the db_connection_uri
    fixture.
    """

    TEST_TABLE_NAME = 'public.test_table'

    reader = DataGridTextReader()

    @fixture(autouse=True)
    def _before_and_after_each_test(self, db_connection: Connection) -> None:
        # Setup:
        db_connection.execute(f'DROP TABLE IF EXISTS {self.TEST_TABLE_NAME}')
        yield  # Test functions will run at this point.
        # Teardown:

    def test_save_as_table_when_data_types_not_specified(
            self,
            db_connection: Connection
    ):
        self.reader.save_as_table(self.TEST_TABLE_NAME, """
        +-------------+----------+------------+-------------------+
        |string_column|int_column|float_column|timestamp_column   |
        +-------------+----------+------------+-------------------+
        # This is a comment that gets ignored.
        |one          |1         |1.1         |2018-01-01 00:00:00| # Another comment to ignore
        |two          |2         |2.2         |2018-01-02 12:34:56|
        +-------------+----------+------------+-------------------+
        """, db_connection)

        actual_rows = self._get_test_table_rows()

        expected_rows = [
            {
                'string_column': 'one',
                'int_column': '1',
                'float_column': '1.1',
                'timestamp_column': '2018-01-01 00:00:00'
            },
            {
                'string_column': 'two',
                'int_column': '2',
                'float_column': '2.2',
                'timestamp_column': '2018-01-02 12:34:56'
            }
        ]
        assert_equal(expected_rows, actual_rows)

    def test_save_as_table_when_row_delimiters_not_present(
            self,
            db_connection: Connection
    ):
        self.reader.save_as_table(self.TEST_TABLE_NAME, """
        |string_column|int_column|float_column|timestamp_column   |
        |one          |1         |1.1         |2018-01-01 00:00:00|
        |two          |2         |2.2         |2018-01-02 12:34:56|
        """, db_connection)

        actual_rows = self._get_test_table_rows()

        expected_rows = [
            {
                'string_column': 'one',
                'int_column': '1',
                'float_column': '1.1',
                'timestamp_column': '2018-01-01 00:00:00'
            },
            {
                'string_column': 'two',
                'int_column': '2',
                'float_column': '2.2',
                'timestamp_column': '2018-01-02 12:34:56'
            }
        ]
        assert_equal(expected_rows, actual_rows)

    def test_save_as_table_when_data_types_specified(
            self,
            db_connection: Connection
    ):
        self.reader.save_as_table(self.TEST_TABLE_NAME, """
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        |string_column|int_column|bigint_column|float_column|timestamp_column   |default_type_column|bool_column|
        [varchar      |int       |bigint       |float       |timestamp          |                   |boolean    ]
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        |one          |1         |1            |1.1         |2018-01-01 00:00:00|11                 |true       |
        |two          |2         |2            |2.2         |2018-01-02 12:34:56|22                 |false      |
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        """, db_connection)

        actual_rows = self._get_test_table_rows()

        expected_rows = [
            {
                'string_column': 'one',
                'int_column': 1,
                'bigint_column': 1,
                'float_column': 1.1,
                'timestamp_column': datetime(2018, 1, 1),
                'default_type_column': '11',
                'bool_column': True
            },
            {
                'string_column': 'two',
                'int_column': 2,
                'bigint_column': 2,
                'float_column': 2.2,
                'timestamp_column': datetime(2018, 1, 2, 12, 34, 56),
                'default_type_column': '22',
                'bool_column': False
            }
        ]
        assert_equal(expected_rows, actual_rows)

    def test_save_as_table_with_multiple_data_type_declarations(
            self,
            db_connection: Connection
    ):
        with raises(ValueError) as exception_info:
            self.reader.save_as_table(self.TEST_TABLE_NAME, """
            +-------------+
            |string_column|
            [varchar      ]
            [varchar      ]
            +-------------+
            |one          |
            +-------------+
            """, db_connection)
        assert ('Cannot have more than one data type declaration line.' ==
                str(exception_info.value))

    def test_save_as_table_when_default_data_type_specified(
            self,
            db_connection: Connection
    ):
        self.reader.save_as_table(self.TEST_TABLE_NAME, """
        +----------+
        |int_column|
        +----------+
        |1         |
        +----------+
        """, db_connection)

        actual_rows = self._get_test_table_rows()

        expected_rows = [{'int_column': '1'}]
        assert_equal(expected_rows, actual_rows)

    def test_save_as_table_when_data_does_not_match_declared_data_type(
            self,
            db_connection: Connection
    ):
        with raises(ValueError) as exception_info:
            self.reader.save_as_table(self.TEST_TABLE_NAME, """
            +----------+
            |int_column|
            [int       ]
            +----------+
            |          | # Empty string is not a valid INT
            +----------+
            """, db_connection)
        assert ("invalid literal for int() with base 10: ''" ==
                str(exception_info.value))

    def test_save_as_table_when_data_does_not_match_default_data_type(
            self,
            db_connection: Connection
    ):
        with raises(ValueError) as exception_info:
            self.reader.save_as_table(self.TEST_TABLE_NAME, """
            +----------+
            |int_column|
            +----------+
            |          | # Empty string is not a valid INT
            +----------+
            """, db_connection, default_data_type='int')
        assert ("invalid literal for int() with base 10: ''" ==
                str(exception_info.value))

    def test_save_as_table_when_default_data_type_overridden(
            self,
            db_connection: Connection
    ):
        self.reader.save_as_table(self.TEST_TABLE_NAME, """
        +-------------+----------+
        |string_column|int_column|
        [varchar      |          ]
        +-------------+----------+
        |1            |1         |
        +-------------+----------+
        """, db_connection, default_data_type='int')

        actual_rows = self._get_test_table_rows()

        expected_rows = [{'string_column': '1', 'int_column': 1}]
        assert_equal(expected_rows, actual_rows)

    def test_save_as_table_when_values_are_null_and_data_types_not_specified(
            self,
            db_connection: Connection
    ):
        self.reader.save_as_table(self.TEST_TABLE_NAME, """
        +---------------+---------------+
        |lower_case_null|upper_case_null|
        +---------------+---------------+
        |null           |NULL           |
        +---------------+---------------+
        """, db_connection)

        actual_rows = self._get_test_table_rows()

        expected_rows = [{'lower_case_null': None, 'upper_case_null': None}]
        assert_equal(expected_rows, actual_rows)

    def test_save_as_table_when_values_are_null_and_data_types_are_specified(
            self,
            db_connection: Connection
    ):
        self.reader.save_as_table(self.TEST_TABLE_NAME, """
        +-------------+----------+-------------+------------+----------------+-------------------+-----------+
        |string_column|int_column|bigint_column|float_column|timestamp_column|default_type_column|bool_column|
        [varchar      |int       |bigint       |float       |timestamp       |                   |boolean    ]
        +-------------+----------+-------------+------------+----------------+-------------------+-----------+
        |null         |NULL      |null         |NULL        |null            |NULL               |null       |
        +-------------+----------+-------------+------------+----------------+-------------------+-----------+
        """, db_connection)

        actual_rows = self._get_test_table_rows()

        expected_rows = [
            {
                'string_column': None,
                'int_column': None,
                'bigint_column': None,
                'float_column': None,
                'timestamp_column': None,
                'default_type_column': None,
                'bool_column': None,
            },
        ]
        assert_equal(expected_rows, actual_rows)

    def test_save_as_table_when_values_are_empty_and_data_types_are_specified(
            self,
            db_connection: Connection
    ):
        self.reader.save_as_table(self.TEST_TABLE_NAME, """
        +-------------+-------------------+
        |string_column|default_type_column|
        [varchar      |                   |
        +-------------+-------------------+
        |             |                   |
        +-------------+-------------------+
        """, db_connection)

        actual_rows = self._get_test_table_rows()

        expected_rows = [{'string_column': '', 'default_type_column': ''}]
        assert_equal(expected_rows, actual_rows)

    def test_save_as_table_with_no_data_rows_and_data_types_not_specified(
            self,
            db_connection: Connection
    ):
        self.reader.save_as_table(self.TEST_TABLE_NAME, """
        +-------------+
        |string_column|
        +-------------+
        +-------------+
        """, db_connection)

        actual_rows = self._get_test_table_rows()
        assert_equal([], actual_rows)

    def test_save_as_table_with_no_data_rows_and_data_types_specified(
            self,
            db_connection: Connection
    ):
        self.reader.save_as_table(self.TEST_TABLE_NAME, """
        +----------+
        |int_column|
        [int       ]
        +----------+
        +----------+
        """, db_connection)

        actual_rows = self._get_test_table_rows()
        assert_equal([], actual_rows)

    def _get_test_table_rows(self):
        rows = self.execute_as_list(f'SELECT * FROM {self.TEST_TABLE_NAME}')
        # In Snowflake, we might get VARIANT, ARRAY or OBJECT columns.
        # If we do, call json.loads() to "rehyd rate" the value:
        # https://docs.snowflake.com/en/user-guide/sqlalchemy.html#variant-array-and-object-support
        for row in rows:
            for key in row:
                value = row[key]
                if isinstance(value, str) and value.startswith('['):
                    row[key] = json.loads(value)
        return rows
