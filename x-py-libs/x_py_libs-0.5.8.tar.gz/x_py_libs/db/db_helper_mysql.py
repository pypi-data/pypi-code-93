from mysql.connector import connect, Error
import pymysql

from enum import Enum
 
from x_py_libs.db import BaseDBHelper

class MySqlConnectTypeEnum(Enum):
    PyMySql = 1
    MySqlConnector = 2

class MySqlDBHelper(BaseDBHelper):

    def connect(self):
        try:
            user = self.params.get('user')
            password = self.params.get('password')
            host = self.params.get('host')
            port = self.params.get('port')
            database = self.params.get('database')

            connect_method = self.params.get('connect_method')

            conn = None
            connect_method = MySqlConnectTypeEnum.PyMySql if connect_method is None else connect_method

            connect_params = {
                'user':user,
                'password': password,
                'host':host,
                'port': int(port),
                'database':database
            }
            connect_func = None

            if connect_method == MySqlConnectTypeEnum.PyMySql:
                connect_func = pymysql.connect;
                connect_params['cursorclass'] = pymysql.cursors.DictCursor
                # conn = pymysql.connect(host, user, password, database, port)
            elif connect_method == MySqlConnectTypeEnum.MySqlConnector:
                connect_func = connect.connect;
                connect_params['dictionary'] = True
                connect_params['use_pure'] = False
                # conn = connect.connect(user=user, password=password,
                #                 host=host,
                #                 port=port,
                #                 database=database,
                #                 use_pure=False)
            conn = connect_func(**connect_params)
            return conn
        except Error as e:
            print(e)
            return None

    def get_list_base(self, table_name, fields, condition='', params=None, order_field='id', order_type='DESC', page_index=0, page_size=10, pagination=True):
        cnt = 0
        if pagination:
            cnt_sql = """SELECT COUNT(1) AS cnt FROM """ + table_name + ' WHERE 1 = 1 ' + condition + """;"""
            rst = self.fetch_one(cnt_sql, params)
            cnt = rst['cnt']

        sql = """SELECT """ + fields + """ FROM """ + table_name
        sql += """ WHERE 1 = 1 """
        sql += condition

        if order_field is not None and order_type is not None:
            order_field = [order_field] if type(order_field) is str else order_field
            order_type = [order_type] if type(order_type) is str else order_type

            if len(order_type) != len(order_field):
                order_type = list(map(lambda x: order_type[0], range(len(order_field))))

            sort_list = list(map(lambda f, t: """ %s %s """ % (f, t), order_field, order_type))

            sql += """ ORDER BY """ + ','.join(sort_list)

        if pagination:
            if page_size > 0:
                sql += """ LIMIT %s OFFSET %s """
                params.append(page_size)
                params.append(page_size*page_index)

        sql += """;"""

        # print(sql, params)

        rst = self.fetch_all(sql, params)
        return rst, cnt

    def fetch_returning_id(self, sql, *params, **kw):

        def callback(cur):
            return cur.lastrowid

        return self.execute_sql(sql, callback, *params, **kw)

    # def fetch_rowcount(self, sql, *params, **kw):
    #     return super().fetch_rowcount(sql, *params, **kw)

    def execute_many(self, sql, *params):
        conn = self.connect()
        cur = conn.cursor()
        rst = cur.executemany(sql, *params)
        conn.commit()
        conn.close()
        # print('rst:',rst)
        return rst

    def execute_sql(self, sql, callback, *params, **kw):
        conn = self.connect()

        if conn == None:
            return None

        # cur = conn.cursor(cursor_factory=RealDictCursor)
        cur = conn.cursor()
        rst = None

        # print('sql:', cur.mogrify(sql, *params))

        cur.execute(sql, *params)

        # rst = cur.fetchone()

        rst = callback(cur)
        conn.commit()
        conn.close()
        # print('rst:',rst)
        return rst

    def callproc(self, proc_name, *params):
        conn = self.connect()

        if conn == None:
            return None

        cur = conn.cursor()
        cur.callproc(proc_name, *params)
        rst = cur.fetchall()

        conn.commit()
        conn.close()
        return rst
