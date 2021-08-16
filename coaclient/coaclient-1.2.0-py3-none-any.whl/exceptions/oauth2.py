"""
CoaClient OAuth2.0 exceptions
"""
from coaclient.exceptions.base import CoaClientBaseException

__all__ = (
    "OAuth2ClientException",
    "OAuth2ConfigError",
    "OAuth2CacheException",
    "OAuth2TokenExpiredError",
)


class OAuth2ClientException(CoaClientBaseException):
    """ OAuth2.0 client exception class for custom exception """
    _STR = "Coursera OAuth2.0 client exception by OAuth2.0 protocol: {message}"


class OAuth2ConfigError(CoaClientBaseException):
    """ Coursera OAuth2.0 Config custom error class """
    _STR = "Coursera OAuth2.0 configuration error: {message}"


class OAuth2CacheException(CoaClientBaseException):
    """ Coursera OAuth2.0 Cache custom exception class """


class OAuth2TokenExpiredError(CoaClientBaseException):
    """ OAuth2.0 token expired error class """
    _STR = "Coursera OAuth2.0 token expired error: {message}"
