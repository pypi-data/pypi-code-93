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

import os
from typing import List

from _pytest.fixtures import FixtureRequest
from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Connection
from sqlalchemy.engine.cursor import CursorResult


class DatabaseTestBase:
    _db_connection = None

    @staticmethod
    def get_required_env_var(variable_name: str):
        value = os.getenv(variable_name)
        if not value:
            raise ValueError(f'Required environment variable "{variable_name}" not found.')
        return value

    @fixture(autouse=True, scope="module")
    def __before_and_after_all_tests(self, db_connection: Connection) -> None:
        # Setup:
        DatabaseTestBase._db_connection = db_connection
        yield  # Test functions will run at this point.
        # Teardown:

    @classmethod
    def execute(cls, query: str) -> CursorResult:
        return cls._db_connection.execute(query)

    @classmethod
    def execute_as_list(cls, query: str) -> List[dict]:
        return [dict(row) for row in cls.execute(query)]

    @fixture(scope="module")
    def db_connection(self, request: FixtureRequest, db_connection_uri) -> Connection:
        """
        Create a SQLAlchemy Connection fixture for testing.
        :param request: pytest FixtureRequest object
        :param db_connection_uri: A SQLAlchemy connection URI
        :return: A SQLAlchemy Connection
        """
        if not db_connection_uri:
            raise ValueError(f'db_connection_uri is required.')
        db_engine = create_engine(db_connection_uri)
        connection = db_engine.connect()
        request.addfinalizer(lambda: connection.close())  # Close connection after all tests have run
        return connection
