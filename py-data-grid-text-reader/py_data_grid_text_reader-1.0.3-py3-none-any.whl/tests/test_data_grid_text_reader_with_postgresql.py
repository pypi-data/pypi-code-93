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

from tests.data_grid_text_reader_test_base import DataGridTextReaderTestBase


@pytest.mark.skip  # To run this test, disable this skip statement.
class TestDataGridTextReaderWithPostgreSQL(DataGridTextReaderTestBase):
    """Runs all of the tests in the superclass."""

    @classmethod
    @pytest.fixture(scope="module")
    def db_connection_uri(cls) -> str:
        """Returns the PostgreSQL-specific database connection URI"""
        return cls.get_required_env_var(
            'PY_DATA_GRID_TEXT_READER_POSTGRESQL_CONNECTION_URI')
