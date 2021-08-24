import logging
import sys
from .setting import THROW_EXCEPTION_ON_ERROR

class PyVException(Exception):
    pass

class InvalidParameterException(PyVException):
    pass

class InvalidAddressException(PyVException):
    pass

class NetworkException(PyVException):
    pass

class MissingPrivateKeyException(PyVException):
    pass

class InsufficientBalanceException(PyVException):
    pass

def set_throw_on_error(throw=True):
    global THROW_EXCEPTION_ON_ERROR
    THROW_EXCEPTION_ON_ERROR = throw

def throw_error(msg, exception=Exception):
    logging.error(msg)
    if THROW_EXCEPTION_ON_ERROR:
        raise exception(msg)
