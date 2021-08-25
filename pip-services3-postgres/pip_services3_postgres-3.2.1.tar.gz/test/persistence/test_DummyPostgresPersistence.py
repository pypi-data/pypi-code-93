# -*- coding: utf-8 -*-

import os

from pip_services3_commons.config import ConfigParams

from test.fixtures.DummyPersistenceFixture import DummyPersistenceFixture
from test.persistence.DummyPostgresPersistence import DummyPostgresPersistence


class TestDummyPostgresPersistence:
    persistence: DummyPostgresPersistence
    fixture: DummyPersistenceFixture

    postgres_uri = os.getenv('POSTGRES_URI')
    postgres_host = os.getenv('POSTGRES_HOST') or 'localhost'
    postgres_port = os.getenv('POSTGRES_PORT') or 5432
    postgres_database = os.getenv('POSTGRES_DB') or 'test'
    postgres_user = os.getenv('POSTGRES_USER') or 'postgres'
    postgres_password = os.getenv('POSTGRES_PASSWORD') or 'postgres'

    @classmethod
    def setup_class(cls):
        if cls.postgres_uri is None and cls.postgres_host is None:
            return
        db_config = ConfigParams.from_tuples(
            'connection.uri', cls.postgres_uri,
            'connection.host', cls.postgres_host,
            'connection.port', cls.postgres_port,
            'connection.database', cls.postgres_database,
            'credential.username', cls.postgres_user,
            'credential.password', cls.postgres_password
        )
        cls.persistence = DummyPostgresPersistence()
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
