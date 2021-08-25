# -*- coding: utf-8 -*-

import os

from pip_services3_commons.config import ConfigParams

from test.fixtures.Dummy2PersistenceFixture import Dummy2PersistenceFixture
from test.persistence.Dummy2MySqlPersistence import Dummy2MySqlPersistence


class TestDummy2MySqlPersistence:
    persistence: Dummy2MySqlPersistence
    fixture: Dummy2PersistenceFixture

    mysql_uri = os.getenv('MYSQL_URI')
    mysql_host = os.getenv('MYSQL_HOST') or 'localhost'
    mysql_port = os.getenv('MYSQL_PORT') or 5432
    mysql_database = os.getenv('MYSQL_DB') or 'test'
    mysql_user = os.getenv('MYSQL_USER') or 'user'
    mysql_password = os.getenv('MYSQL_PASSWORD') or 'password'

    def setup_method(self):
        if self.mysql_uri is None and self.mysql_host is None:
            return
        db_config = ConfigParams.from_tuples(
            'connection.uri', self.mysql_uri,
            'connection.host', self.mysql_host,
            'connection.port', self.mysql_port,
            'connection.database', self.mysql_database,
            'credential.username', self.mysql_user,
            'credential.password', self.mysql_password
        )
        self.persistence = Dummy2MySqlPersistence()
        self.fixture = Dummy2PersistenceFixture(self.persistence)
        self.persistence.configure(db_config)
        self.persistence.open(None)

        self.persistence.clear(None)

    def teardown_method(self):
        self.persistence.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()

    def test_batch_operations(self):
        self.fixture.test_batch_operations()
