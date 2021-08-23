#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from pywkdb.utils.db_base import DbBase
logger = logging.getLogger('MySQLDb')


class MySQLDb(DbBase):

    def __init__(self, url, with_tran=False):
        """
        构造函数,初始化数据库连接
        :param url: example mssql://sa:123456@127.0.0.1:1443/dbname?charset=utf-8
        :param with_tran:
        """
        super(MySQLDb, self).__init__(url, with_tran)


if __name__ == '__main__':
    pass
