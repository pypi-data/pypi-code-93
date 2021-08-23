#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from pywkdb.utils.db_base import DbBase
from pywkdb.utils.url_parse import UrlParse
logger = logging.getLogger('MySQLDb')


class MsSQLDb(DbBase):

    def __init__(self, url, with_tran=False):
        """
        构造函数,初始化数据库连接
        :param url: example mssql://root:123456@127.0.0.1:3306/dbname?charset=utf-8
        :param with_tran:
        """
        super(MsSQLDb, self).__init__(url, with_tran)


if __name__ == '__main__':
    pass
