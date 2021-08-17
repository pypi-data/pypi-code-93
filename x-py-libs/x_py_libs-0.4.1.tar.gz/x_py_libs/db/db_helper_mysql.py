from mysql.connector import connect, Error

from x_py_libs.db import BaseDBHelper

class MySqlDBHelper(BaseDBHelper):

    def connect(self):
        try:
            user = self.params.get('user')
            password = self.params.get('password')
            host = self.params.get('host')
            database = self.params.get('database')
            conn = connect.connect(user=user, password=password,
                              host=host,
                              database=database,
                              use_pure=False)
            return conn
        except Error as e:
            print(e)
            return None
