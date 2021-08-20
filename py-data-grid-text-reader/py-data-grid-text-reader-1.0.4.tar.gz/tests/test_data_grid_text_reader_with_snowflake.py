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

from tests.data_grid_text_reader_test_base import DataGridTextReaderTestBase


@pytest.mark.skip  # To run this test, disable this skip statement.
class TestDataGridTextReaderWithSnowflake(DataGridTextReaderTestBase):
    """Runs all of the tests in the superclass."""

    @classmethod
    @pytest.fixture(scope="module")
    def db_connection_uri(cls) -> str:
        """Returns the Snowflake-specific database connection URI"""
        return cls.get_required_env_var(
            'PY_DATA_GRID_TEXT_READER_SNOWFLAKE_CONNECTION_URI')

    def test_save_as_table_with_array_column(
            self,
            db_connection: Connection
    ):
        """Test using the Snowflake ARRAY data type"""
        self.reader.save_as_table(self.TEST_TABLE_NAME, """
        +----------------------+
        |array_column_with_null|
        [array                 |
        +----------------------+
        |null                  |
        +----------------------+
        """, db_connection)
        # TODO: Support array columns that contain non-null values, such as:
        # +----------------------+
        # |array_column_with_ints|
        # [array                 |
        # +----------------------+
        # |[-1, 0, 1]            |
        # +----------------------+

        actual_rows = self._get_test_table_rows()
        assert [{'array_column_with_null': None}] == actual_rows
