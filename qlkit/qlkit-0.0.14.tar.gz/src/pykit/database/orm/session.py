#!/usr/bin/env python
# -*- coding:utf-8 -*-

import abc


class Session(abc.ABC):

    # transaction
    @abc.abstractmethod
    def commit(self):
        pass

    @abc.abstractmethod
    def rollback(self):
        pass

    @abc.abstractmethod
    def begin(self):
        pass

    @abc.abstractmethod
    def remove(self):
        pass

    # session
    @abc.abstractmethod
    def query(self):
        pass

    @abc.abstractmethod
    def add(self):
        pass

    @abc.abstractmethod
    def create(self, persistent_object):
        """将PO持久化，并且将新的数据同步到persistent_object中。如主键值或创建时间等"""
        pass

    @abc.abstractmethod
    def close(self):
        pass
