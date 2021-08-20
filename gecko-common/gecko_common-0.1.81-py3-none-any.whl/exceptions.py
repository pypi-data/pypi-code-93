"""
This module contains the set of AssetMove' exceptions.
"""


class BasicException(Exception):
    def __init__(self, *args, **kwargs):
        super(BasicException, self).__init__(*args, **kwargs)


class SystemUnNormal(BasicException):
    """系统不可用,维护中"""


class InsufficientBalance(BasicException):
    """账户余额不足"""


class TradePairUnavailable(BasicException):
    """交易对维护"""


class UnknownError(BasicException):
    """未知错误"""


class HuoBiWebSocketError(BasicException):
    """WS错误"""


class OkexWebSocketError(BasicException):
    """WS错误"""
