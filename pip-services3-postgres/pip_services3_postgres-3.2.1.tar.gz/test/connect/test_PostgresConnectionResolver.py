# -*- coding: utf-8 -*-

from pip_services3_commons.config import ConfigParams

from pip_services3_postgres.connect.PostgresConnectionResolver import PostgresConnectionResolver


class TestPostgresConnectionResolver:

    def test_connection_config(self):
        db_config = ConfigParams.from_tuples(
            'connection.host', 'localhost',
            'connection.port', 5432,
            'connection.database', 'test',
            'connection.ssl', True,
            'credential.username', 'postgres',
            'credential.password', 'postgres',
        )

        resolver = PostgresConnectionResolver()
        resolver.configure(db_config)

        config = resolver.resolve(None)

        assert config is not None
        assert 'localhost' == config['host']
        assert 5432 == config['port']
        assert 'test' == config['dbname']
        assert 'postgres' == config['user']
        assert 'postgres' == config['password']
        assert config.get('ssl') is None
