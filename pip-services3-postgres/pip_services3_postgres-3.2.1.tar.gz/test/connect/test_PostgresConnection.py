# -*- coding: utf-8 -*-

import os

from pip_services3_commons.config import ConfigParams

from pip_services3_postgres.connect.PostgresConnection import PostgresConnection


class TestPostgresConnection:
    connection: PostgresConnection = None

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
        cls.connection = PostgresConnection()
        cls.connection.configure(db_config)

        cls.connection.open(None)

    @classmethod
    def teardown_class(cls):
        cls.connection.close(None)

    def test_open_and_close(self):
        assert self.connection.get_connection() is not None
        assert isinstance(self.connection.get_database_name(), str)
