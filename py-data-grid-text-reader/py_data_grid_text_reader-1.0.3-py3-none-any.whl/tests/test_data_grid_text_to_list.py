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

from pytest import raises

from data_grid_text_reader.data_grid_text_reader import DataGridTextReader


class TestDataGridTextToList:
    reader = DataGridTextReader()

    def test_data_grid_text_to_list_when_data_types_not_specified(self):
        actual = self.reader.data_grid_text_to_list("""
        +-------------+----------+------------+-------------------+
        |string_column|int_column|float_column|timestamp_column   |
        +-------------+----------+------------+-------------------+
        # This is a comment that gets ignored.
        |one          |1         |1.1         |2018-01-01 00:00:00| # Another comment to ignore
        |two          |2         |2.2         |2018-01-02 12:34:56|
        +-------------+----------+------------+-------------------+
        """)

        expected = [
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
        assert expected == actual

    def test_data_grid_text_to_list_when_data_types_specified(self):
        actual = self.reader.data_grid_text_to_list("""
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        |string_column|int_column|bigint_column|float_column|timestamp_column   |default_type_column|bool_column|
        [varchar      |int       |bigint       |float       |timestamp          |                   |boolean    ]
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        |one          |1         |1            |1.1         |2018-01-01 00:00:00|11                 |true       |
        |two          |2         |2            |2.2         |2018-01-02 12:34:56|22                 |false      |
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        """)

        expected = [
            {
                'string_column': 'one',
                'int_column': 1,
                'bigint_column': 1,
                'float_column': 1.1,
                'timestamp_column': datetime(2018, 1, 1, 0, 0),
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
        assert expected == actual

    def test_data_grid_text_to_list_when_no_rows_specified(self):
        actual = self.reader.data_grid_text_to_list("""
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        |string_column|int_column|bigint_column|float_column|timestamp_column   |default_type_column|bool_column|
        [varchar      |int       |bigint       |float       |timestamp          |                   |boolean    ]
        +-------------+----------+-------------+------------+-------------------+-------------------+-----------+
        """)

        assert [] == actual

    def test_data_grid_text_to_list_when_row_delimiters_not_present(self):
        actual = self.reader.data_grid_text_to_list("""
        |string_column|int_column|float_column|timestamp_column   |
        |one          |1         |1.1         |2018-01-01 00:00:00|
        |two          |2         |2.2         |2018-01-02 12:34:56|
        """)

        expected = [
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
        assert expected == actual

    def test_data_grid_text_to_list_when_grid_text_is_empty(self):
        with raises(ValueError) as exception_info:
            self.reader.data_grid_text_to_list('')
        assert ('data_grid_text is required.' == str(exception_info.value))

    def test_data_grid_text_to_list_when_no_grid_text_supplied(self):
        with raises(ValueError) as exception_info:
            self.reader.data_grid_text_to_list(None)
        assert ('data_grid_text is required.' == str(exception_info.value))

    def test_data_grid_text_to_list_with_multiple_data_type_declarations(self):
        with raises(ValueError) as exception_info:
            self.reader.data_grid_text_to_list("""
            +-------------+
            |string_column|
            [varchar      ]
            [varchar      ]
            +-------------+
            |one          |
            +-------------+
            """)
        assert ('Cannot have more than one data type declaration line.' ==
                str(exception_info.value))
