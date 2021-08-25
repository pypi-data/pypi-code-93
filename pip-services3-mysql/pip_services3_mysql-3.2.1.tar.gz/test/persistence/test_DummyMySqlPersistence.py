# -*- coding: utf-8 -*-

import os

from pip_services3_commons.config import ConfigParams

from test.fixtures.DummyPersistenceFixture import DummyPersistenceFixture
from test.persistence.DummyMySqlPersistence import DummyMySqlPersistence


class TestDummyMySqlPersistence:
    persistence: DummyMySqlPersistence
    fixture: DummyPersistenceFixture

    mysql_uri = os.getenv('MYSQL_URI')
    mysql_host = os.getenv('MYSQL_HOST') or 'localhost'
    mysql_port = os.getenv('MYSQL_PORT') or 5432
    mysql_database = os.getenv('MYSQL_DB') or 'test'
    mysql_user = os.getenv('MYSQL_USER') or 'user'
    mysql_password = os.getenv('MYSQL_PASSWORD') or 'password'

    @classmethod
    def setup_class(cls):
        if cls.mysql_uri is None and cls.mysql_host is None:
            return
        db_config = ConfigParams.from_tuples(
            'connection.uri', cls.mysql_uri,
            'connection.host', cls.mysql_host,
            'connection.port', cls.mysql_port,
            'connection.database', cls.mysql_database,
            'credential.username', cls.mysql_user,
            'credential.password', cls.mysql_password
        )
        cls.persistence = DummyMySqlPersistence()
        cls.fixture = DummyPersistenceFixture(cls.persistence)

        cls.persistence.configure(db_config)
        cls.persistence.open(None)

    @classmethod
    def teardown_class(cls):
        cls.persistence.close(None)

    def setup_method(self):
        self.persistence.clear(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()

    def test_batch_operations(self):
        self.fixture.test_batch_operations()
