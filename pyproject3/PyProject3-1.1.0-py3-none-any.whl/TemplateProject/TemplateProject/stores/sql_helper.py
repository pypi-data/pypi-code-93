#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/19 11:15
# @Author  : 江斌
# @Software: PyCharm

import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def to_unicode_ascii(s):
    return json.dumps(s).replace('"', '')


def to_unicode_ascii2(s):
    return s.encode('unicode-escape').decode()


class SqlHelper(object):
    def __init__(self, conn_str, ):
        self.engine = create_engine(
            fr'sqlite:///{conn_str}',
            echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_all_table(self, base):
        base.metadata.create_all(self.engine)

    def execute(self, sql):
        """
        执行原生SQL。
        :param sql:
        :return:
        """
        conn = self.engine.raw_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        cursor.close()  # 需要手动关闭？？
        conn.close()  # 需要手动关闭？？
        return result
