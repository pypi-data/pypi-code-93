from functools import lru_cache

import psycopg2
from psycopg2.extras import RealDictCursor


class SQLConnector:

    def __init__(self, **kwargs):
        self.endpoint = kwargs['endpoint']
        self.database = kwargs['database']
        self.user = kwargs['user']
        self.password = kwargs['password']
        self.port = kwargs['port']
        self.connection = None

    @lru_cache(maxsize=128)
    def connect(self):
        try:
            if not self.connection:
                self.connection = psycopg2.connect(
                    dbname=self.database,
                    host=self.endpoint,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                )
            self.connection.set_session(autocommit=True)
            return self.connection
        except Exception as error:
            print(error)
            raise error

    @lru_cache(maxsize=128)
    def cursor(self):
        return self.connection.cursor(cursor_factory=RealDictCursor)
