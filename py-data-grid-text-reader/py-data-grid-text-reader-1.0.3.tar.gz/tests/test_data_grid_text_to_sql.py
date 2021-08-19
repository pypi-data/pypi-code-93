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

from pytest import raises

from data_grid_text_reader.data_grid_text_reader import DataGridTextReader
from data_grid_text_reader.text_util import strip_lines


class TestDataGridTextToSQL:
    TEST_TABLE_NAME = 'public.test_table'

    reader = DataGridTextReader()

    def test_data_grid_text_to_sql_when_data_types_not_specified(self):
        actual = self.reader.data_grid_text_to_sql(self.TEST_TABLE_NAME, """
        +-------------+----------+------------+-------------------+
        |string_column|int_column|float_column|timestamp_column   |
        +-------------+----------+------------+-------------------+
        # This is a comment that gets ignored.
        |one          |1         |1.1         |2018-01-01 00:00:00| # Another comment to ignore
        |two          |2         |2.2         |2018-01-02 12:34:56|
        +-------------+----------+------------+-------------------+
        """)

        expected = (
            strip_lines("""
            CREATE OR REPLACE TABLE public.test_table(
                    string_column varchar,
                    int_column varchar,
                    float_column varchar,
                    timestamp_column varchar
            );
            """),
            strip_lines("""
            INSERT INTO public.test_table
            (string_column, int_column, float_column, timestamp_column) VALUES
            ('one', '1', '1.1', '2018-01-01 00:00:00'),
            ('two', '2', '2.2', '2018-01-02 12:34:56');
            """)
        )
        assert expected == actual

    def test_data_grid_text_to_sql_when_data_types_specified(self):
        actual = self.reader.data_grid_text_to_sql(self.TEST_TABLE_NAME, """
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        |string_column|int_column|bigint_column|float_column|timestamp_column   |default_type_column|bool_column|
        [varchar      |int       |bigint       |float       |timestamp          |                   |boolean    ]
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        |one          |1         |1            |1.1         |2018-01-01 00:00:00|11                 |true       |
        |two          |2         |2            |2.2         |2018-01-02 12:34:56|22                 |false      |
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        """)

        expected = (
            strip_lines("""
                CREATE OR REPLACE TABLE public.test_table(
                        string_column varchar,
                        int_column int,
                        bigint_column bigint,
                        float_column float,
                        timestamp_column timestamp,
                        default_type_column varchar,
                        bool_column boolean
                );
                """),
            strip_lines("""
                INSERT INTO public.test_table
                (string_column, int_column, bigint_column, float_column, timestamp_column, default_type_column, bool_column) VALUES
                ('one', 1, 1, 1.1, '2018-01-01 00:00:00', '11', TRUE),
                ('two', 2, 2, 2.2, '2018-01-02 12:34:56', '22', FALSE);
                """)
        )
        assert expected == actual

    def test_data_grid_text_to_sql_when_no_rows_specified(self):
        actual = self.reader.data_grid_text_to_sql(self.TEST_TABLE_NAME, """
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        |string_column|int_column|bigint_column|float_column|timestamp_column   |default_type_column|bool_column|
        [varchar      |int       |bigint       |float       |timestamp          |                   |boolean    ]
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        """)

        expected = (
            strip_lines("""
                CREATE OR REPLACE TABLE public.test_table(
                        string_column varchar,
                        int_column int,
                        bigint_column bigint,
                        float_column float,
                        timestamp_column timestamp,
                        default_type_column varchar,
                        bool_column boolean
                );
                """),
            None  # There are no rows to insert.
        )
        assert expected == actual

    def test_data_grid_text_to_sql_when_no_table_name_supplied(self):
        with raises(ValueError) as exception_info:
            self.reader.data_grid_text_to_sql(None, None)
        assert ('table_name is required.' == str(exception_info.value))

    def test_data_grid_text_to_sql_when_no_grid_text_supplied(self):
        with raises(ValueError) as exception_info:
            self.reader.data_grid_text_to_sql(self.TEST_TABLE_NAME, None)
        assert ('data_grid_text is required.' == str(exception_info.value))
