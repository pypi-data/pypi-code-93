#!/usr/bin/env python
# -*- coding:utf-8 -*-

# for other package import
from . import error_pb2
from .error_pb2 import Error
from . import code_pb2
from . import error_reason_pb2
from .error_reason_pb2 import ERROR_REASON_UNSPECIFIED

# for self use
from ..cmd import app_local
from functools import wraps


class ErrorProxy(object):

    error_check_func_name = ["is_%s" % code_name.lower() for code_name in code_pb2.Code.keys()]

    class InnerError(object):
        def __init__(self, error):
            self.error = error

    def __init__(self, error: Error):
        self.inner = self.InnerError(error)
        for name, value in code_pb2.Code.items():
            func_name = "is_%s" % name.lower()
            # inject error check function into error proxy object
            setattr(self, func_name, checker_wrapper(name, error.code))

    def __getattr__(self, item):
        if item in self.error_check_func_name:
            return getattr(self, item)
        else:
            return getattr(self.inner.error, item)

    def __str__(self):
        # call error.__str__()
        return self.inner.error.__str__()


def new_error(code: int, reason: int,
              message="", localized_message="",
              metadata: dict = None) -> error_pb2.Error:
    """

    :param code:
    :param message:
    :param reason:
    :param localized_message:
    :param metadata: data format {"key": "value"}
    :return:
    """
    if metadata is None:
        metadata = {}
    else:
        # check metadata data type
        for k, v in metadata.items():
            if not isinstance(k, (str, bytes)):
                raise TypeError("metadata key must be bytes or unicode")
            if not isinstance(v, (str, bytes)):
                raise TypeError("metadata value must be bytes or unicode")

    # add biz_id
    if "biz_id" not in metadata and app_local.biz_id:
        metadata["biz_id"] = app_local.biz_id

    err_pb = error_pb2.Error(
        code=code,
        message=message,
        reason=reason,
        localized_message=localized_message,
        metadata=metadata
    )
    err = ErrorProxy(err_pb)

    return err


def checker_wrapper(name, code_value):
    """
    为Error对象注入错误检测的函数：error.is_internal() error.is_not_found() etc..
    函数名的格式为 is_some_error() 具体的名字对应error/code.proto
    :param name:
    :param code_value:
    :return:
    """
    @wraps(checker_wrapper)
    def code_check():
        return code_value == code_pb2.Code.Value(name)
    return code_check
