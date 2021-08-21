#!/usr/bin/env python
# -*- coding:utf-8 -*-

import inspect
from typing import Any

from functools import wraps
from .framework import ApplicationService
from ..database.transaction import TransactionFactory
from ..error import new_error
from ..error import code_pb2


class ApplicationTransactionalService(ApplicationService):

    def __init__(self, transaction_factory: TransactionFactory):
        self.transaction_factory = transaction_factory


def transaction_handler(application_func):
    """
    为DDD模块中ApplicationService的方法提供数据库事务支持。
    这个方法会负责管理事务：创建、提交、回滚。
    同时，会保持方法的返回格式：(Response, Error)
    :param application_func:
    :return:
    """
    @wraps(application_func)
    def execute_transaction_flow(application_obj: ApplicationTransactionalService, request):

        # setup transaction
        session = application_obj.transaction_factory.get_transaction()
        session.begin()

        response = None
        # err = new_error(code_pb2.UNKNOWN, "transaction_handler_default_err")
        err = None
        try:
            response, err = application_func(application_obj, request)
            if err:
                session.rollback()
            else:
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        else:
            return response, err
        finally:
            # remove session from Thread Local
            application_obj.transaction_factory.remove()
    return execute_transaction_flow


class SessionRepository(object):
    def __init__(self, session_factory: TransactionFactory):
        self.session_factory = session_factory

    @property
    def session(self):
        return self.session_factory.get_transaction()

    def cover_to(self, query_res: Any) -> Any:
        if not hasattr(self, 'MAPPING'):
            return query_res
        do = self.MAPPING['do']
        po = self.MAPPING['po']
        options = self.MAPPING['options']

        if isinstance(query_res, list):
            res = []
            for query_obj in query_res:
                if not isinstance(query_obj, po):
                    break
                res.append(self.po2do(do, query_res, options["field_mapping"]))
            return res

        elif isinstance(query_res, po):
            return self.po2do(do, query_res, options["field_mapping"])
        return query_res

    @classmethod
    def po2do(cls, do: Any, query_obj: Any, field_mapping: dict) -> Any:
        # domain object init params
        keys = list(inspect.signature(do.__init__).parameters.keys())[1:]
        args = {key: getattr(query_obj, key, None) for key in keys}

        option_po_fields = field_mapping["po"]
        option_do_fields = field_mapping["do"]
        option_args = {}

        for i, v in enumerate(option_do_fields):
            option_args[v] = getattr(query_obj, option_po_fields[i])

        args.update(option_args)
        instance = do(**args)
        return instance
