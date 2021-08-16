#!/usr/bin/env python
# -*- coding:utf-8 -*-

import abc
from contextlib import ContextDecorator


class Transaction(abc.ABC):
    """
    Database Transaction Interface
    """

    @abc.abstractmethod
    def begin(self):
        pass

    @abc.abstractmethod
    def commit(self):
        pass

    @abc.abstractmethod
    def rollback(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass


class TransactionFactory(abc.ABC):

    @abc.abstractmethod
    def get_transaction(self) -> Transaction:
        pass


class TransactionHook(abc.ABC):

    @abc.abstractmethod
    def before_begin(self):
        pass

    @abc.abstractmethod
    def after_begin(self):
        pass

    @abc.abstractmethod
    def before_commit(self):
        pass

    @abc.abstractmethod
    def after_commit(self):
        pass

    @abc.abstractmethod
    def before_rollback(self):
        pass

    @abc.abstractmethod
    def after_rollback(self):
        pass


class TransactionEmptyHook(TransactionHook):

    def before_begin(self):
        pass

    def after_begin(self):
        pass

    def before_commit(self):
        pass

    def after_commit(self):
        pass

    def before_rollback(self):
        pass

    def after_rollback(self):
        pass


class TransactionManager(ContextDecorator, Transaction):

    def __init__(self, transaction: Transaction, hook: TransactionHook = None):
        self.transaction = transaction
        self.hook = TransactionEmptyHook() if hook is None else hook

    # for context manager

    def __enter__(self):
        self.begin()

        return self.transaction

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
            return True
        else:
            self.rollback()
            return False

    def begin(self):
        self.hook.before_begin()
        self.transaction.begin()
        self.hook.after_begin()

    def commit(self):
        self.hook.before_commit()
        self.transaction.commit()
        self.hook.after_commit()

    def rollback(self):
        self.hook.before_rollback()
        self.transaction.rollback()
        self.hook.after_rollback()

    def close(self):
        pass


"""
Usecase 1, transaction as decorator:

@TransactionManager(transaction)
def usecase(self):
    # do some something

    if not data.validate():
        raise IntegrityError()

    # do other thing without integrity error


Usecase 2, transaction as ContextManager:

def usecase(self):
    # do some something
    with TransactionManager(transaction):
        # do some something

        if not data.validate():
        raise IntegrityError()

Usecase 3, low level transaction control:
def usecase(self):
    t = TransactionManager(transaction):
    # do something

    t.begin()

    # do something

    if data.validate():
        t.commit()
    else:
        t.rollback()
"""
