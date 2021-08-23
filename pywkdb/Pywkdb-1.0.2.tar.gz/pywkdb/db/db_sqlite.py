#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from pywkdb.utils.db_base import DbBase
logger = logging.getLogger('SqliteDb')


class SqliteDb(DbBase):

    def __init__(self, url, with_tran=False):
        """
        构造函数,初始化数据库连接
        :param url: example sqlite://:/d:/data/dbfile.db
                             sqlite://://root/data/dbfile.db
        :param with_tran:
        """
        super(SqliteDb, self).__init__(url, with_tran)

    def insert(self, sql: str, params=None):
        """
        插入一条记录
        :param sql:     sql代码
        :param params:  传递参数
        :return:        主键ID
        """
        cur = None
        conn = None
        try:
            conn = self._get_conn()
            cur = self._execute(conn, sql, params)
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            logger.error("insert_error:{}".format(e))
        finally:
            self.close(cur)
            if not self._with_tran:
                self.close(conn)


if __name__ == '__main__':
    pass
