from mysql.connector import connect, Error

from x_py_libs.db import BaseDBHelper

class MySqlDBHelper(BaseDBHelper):

    def connect(self):
        try:
            user = self.params.get('user')
            password = self.params.get('password')
            host = self.params.get('host')
            port = self.params.get('port')
            database = self.params.get('database')
            conn = connect.connect(user=user, password=password,
                              host=host,
                              port=port,
                              database=database,
                              use_pure=False)
            return conn
        except Error as e:
            print(e)
            return None


    def get_list(self, table_name, fields, conditions=None, rawConditions='', order_field='id', order_type='DESC', page_index=0, page_size=10, pagination=True):
        params = []
        condition = ''
        rst = None
        cnt = 0

        if conditions is not None:

            for c in conditions:
                __cc = ''
                template = ''
                t = type(c)

                if t is not list:
                    c = [c]
                    template = '%s'
                else:
                    template = ' AND (%s) '

                for c2 in c:
                    __params, __condition = self.__analyze_condition(c2)
                    params.extend(__params)
                    __cc += __condition
                # print('__cc:', __cc)

                condition += template % __cc
        
        if rawConditions != '':
            condition += rawConditions

        rst, cnt = self.get_list_base(table_name, fields, condition, params, order_field=order_field, order_type=order_type, page_index=page_index, page_size=page_size, pagination=pagination)
        return rst, cnt

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
        sql = sql + """ SELECT LAST_INSERT_ID();"""

        def callback(cur):
            rst = cur.fetchone()
            id = rst.get('id')
            return 0 if id is None else id

        return self.execute_sql(sql, callback, *params, **kw)
