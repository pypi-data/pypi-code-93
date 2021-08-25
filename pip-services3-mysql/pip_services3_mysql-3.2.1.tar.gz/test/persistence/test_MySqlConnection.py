# -*- coding: utf-8 -*-

import os

from pip_services3_commons.config import ConfigParams

from pip_services3_mysql.connect.MySqlConnection import MySqlConnection


class TestMySqlConnection:
    connection: MySqlConnection = None

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
        cls.connection = MySqlConnection()
        cls.connection.configure(db_config)

        cls.connection.open(None)

    @classmethod
    def teardown_class(cls):
        cls.connection.close(None)

    def test_open_and_close(self):
        assert self.connection.get_connection() is not None
        assert isinstance(self.connection.get_database_name(), str)
