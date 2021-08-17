#!/usr/bin/env python
# -*- coding:utf-8 -*-


"""
参考Python Database API 规范的异常设计：https://www.python.org/dev/peps/pep-0249/#exceptions

设计哲学
本异常模块是所有需要使用的第三方数据库模块的异常的超集，如果需要接入新的数据库模块，需要将该模
块的异常映射到本异常体系中。

这样做的好处是：在开发过程中，只需要关心PyKit的异常，而不用关心所选择的持久化方案的异常。这可以
我们将持久化机制与数据访问层隔离开。

"""


class StandardError(Exception):
    """Root Exception"""
    pass


class Warning(Warning, StandardError):
    """
    Exception raised for important warnings like data truncations while
    inserting, etc
    """
    pass


class Error(StandardError):
    """
    Exception that is the base class of all other error exceptions. You can use
    this to catch all errors with one single except statement. Warnings are
    not considered errors and thus should not use this class as base.
    """
    pass


class InterfaceError(Error):
    """
    Exception raised for errors that are related to the database interface
    rather than the database itself.
    """
    pass


class DatabaseError(Error):
    """
    Exception raised for errors that are related to the database.
    """
    pass


class DataError(DatabaseError):
    """
    Exception raised for errors that are due to problems with the processed
    data like division by zero, numeric value out of range, etc.
    """
    pass


class OperationalError(DatabaseError):
    """
    Exception raised for errors that are related to the database's operation
    and not necessarily under the control of the programmer, e.g.
    an unexpected disconnect occurs,
    the data source name is not found,
    a transaction could not be processed,
    a memory allocation error occurred during processing, etc.
    """
    pass


class IntegrityError(DatabaseError):
    """
    Exception raised when the relational integrity of the database is affected,
    e.g. a foreign key check fails.
    """
    pass


class InternalError(DatabaseError):
    """
    Exception raised when the database encounters an internal error, e.g.
    the cursor is not valid anymore, the transaction is out of sync, etc.
    """


class ProgramingError(DatabaseError):
    """
    Exception raised for programming errors, e.g.
    table not found or already exists,
    syntax error in the SQL statement,
    wrong number of parameters specified, etc.
    """
    pass


class NotSupportedError(DatabaseError):
    """
    Exception raised in case a method or database API was used which is not
    supported by the database, e.g.
    requesting a .rollback() on a connection that does not support transaction
    or has transactions turned off.
    """
    pass
