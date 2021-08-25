# -*- coding: utf-8 -*-
from pip_services3_commons.config import ConfigParams

from pip_services3_mysql.connect.MySqlConnectionResolver import MySqlConnectionResolver


class TestMySqlConnectionResolver:

    def test_connection_config(self):
        db_config = ConfigParams.from_tuples(
            'connection.host', 'localhost',
            'connection.port', 3306,
            'connection.database', 'test',
            'connection.ssl', False,
            'credential.username', 'mysql',
            'credential.password', 'mysql',
        )

        resolver = MySqlConnectionResolver()
        resolver.configure(db_config)

        uri = resolver.resolve(None)

        assert isinstance(uri, str)
        assert uri == 'mysql://mysql:mysql@localhost:3306/test?ssl=False'
