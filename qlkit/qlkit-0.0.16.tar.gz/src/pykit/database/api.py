#!/usr/bin/env python
# -*- coding:utf-8 -*-

import abc


class Cursor(abc.ABC):

    @abc.abstractmethod
    def close(self):
        """
        :exception Error or subclass
        :return:
        """
        pass

    @abc.abstractmethod
    def execute(self, operation, params):
        pass

    @abc.abstractmethod
    def executemany(self, operation, seq_of_params):
        pass

    @abc.abstractmethod
    def fetchone(self):
        """
        :exception Error or subclass: if .execute*() did not produce any result
        set or no call was issued yet.
        :return:
        """
        pass

    @abc.abstractmethod
    def fetchmany(self, size):
        """
        :exception Error or subclass: if .execute*() did not produce any result
        set or no call was issued yet.
        :param size:
        :return:
        """
        pass

    @abc.abstractmethod
    def fetchall(self):
        """
        :exception Error or subclass: if .execute*() did not produce any result
        set or no call was issued yet.
        :return:
        """
        pass

    @abc.abstractmethod
    def setinputsizes(self, sizes):
        pass

    @abc.abstractmethod
    def setoutputsize(self, sizes, column):
        pass


class Connection(abc.ABC):

    @abc.abstractmethod
    def close(self):
        """
        https://www.python.org/dev/peps/pep-0249/#Connection.close
        :exception Error or Subclass
        """
        pass

    @abc.abstractmethod
    def commit(self):
        pass

    @abc.abstractmethod
    def rollback(self):
        pass

    @abc.abstractmethod
    def cursor(self) -> Cursor:
        pass


class ConnectionFactory(abc.ABC):

    @abc.abstractmethod
    def new_connection(self, connection_options: dict) -> Connection:
        """
        Database Connection constructors
        :param connection_options: mysql client options
        :return:
        """
        pass


class RepositoryTemplate(object):
    """
    数据访问的通用模版。
    通用的数据处理流程：
        1、初始化资源；
        2、开始事务；
        3、事务中执行请求；
        4、返回数据；
        5、提交/回滚事务；
        6、关闭资源，处理异常
    """
    pass


class CRUDRepository(object):
    pass


class PagingAndSortingRepository(object):
    pass
