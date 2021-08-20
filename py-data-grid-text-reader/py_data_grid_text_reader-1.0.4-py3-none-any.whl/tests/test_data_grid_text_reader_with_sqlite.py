# Copyright 2021 The Data Text Grid Reader Authors. All Rights Reserved.
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

import pytest
from sqlalchemy.engine.base import Connection

from data_grid_text_reader.assert_equal_lists import assert_equal
from tests.data_grid_text_reader_test_base import DataGridTextReaderTestBase


class TestDataGridTextReaderWithSQLite(DataGridTextReaderTestBase):
    """Runs all of the tests in the superclass."""

    @staticmethod
    @pytest.fixture(scope="module")
    def db_connection_uri() -> str:
        """Returns the SQLite-specific database connection URI"""
        return 'sqlite://'

    @pytest.fixture(autouse=True, scope='module')
    def _before_and_after_all_tests(self, db_connection: Connection) -> None:
        # Setup:
        db_connection.execute("ATTACH main AS public")
        yield  # Test functions will run at this point.
        # Teardown:

    def test_save_as_table_when_data_types_specified(
            self,
            db_connection: Connection
    ):
        """
        Overwrite test method from the base class to accommodate differences in
        how dates and times are stored in SQLite.
        From https://www.sqlite.org/datatype3.html:

        "SQLite does not have a storage class set aside for storing dates
        and/or times. Instead, the built-in Date And Time Functions of SQLite
        are capable of storing dates and times as TEXT, REAL, or INTEGER
        values."
        """
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
                'timestamp_column': '2018-01-01 00:00:00',
                'default_type_column': '11',
                'bool_column': True
            },
            {
                'string_column': 'two',
                'int_column': 2,
                'bigint_column': 2,
                'float_column': 2.2,
                'timestamp_column': '2018-01-02 12:34:56',
                'default_type_column': '22',
                'bool_column': False
            }
        ]
        assert_equal(expected_rows, actual_rows)
