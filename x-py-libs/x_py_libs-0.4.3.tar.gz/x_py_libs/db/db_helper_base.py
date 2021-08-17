# -*- coding=utf-8 -*-

class BaseDBHelper(object):

    connect_string = ''
    cur = None
    params = None

    def __init__(self, connect_string, **params):
        self.connect_string = connect_string
        self.params = params

    def connect(self):
        pass


    def fetch_returning_id(self, sql, *params, **kw):
        pass

    def fetch_rowcount(self, sql, *params, **kw):
        def callback(cur):
            # print('cur:',cur)
            return cur.rowcount

        return self.execute_sql(sql, callback, *params, **kw)

    def fetch_one(self, sql, *params, **kw):
        def callback(cur):
            return cur.fetchone()

        return self.execute_sql(sql, callback, *params, **kw)

    def fetch_all(self, sql, *params, **kw):
        def callback(cur):
            return cur.fetchall()

        return self.execute_sql(sql, callback, *params, **kw)

    def execute_sql(self, sql, callback, *params, **kw):
        pass

    def callproc(self, proc_name, *params):
        pass
