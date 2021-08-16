"""
CoaClient exceptions
"""
from coaclient.exceptions.base import CoaClientBaseException
from coaclient.exceptions.commands import CoaClientCommandException
from coaclient.exceptions.oauth2 import (
    OAuth2ClientException,
    OAuth2ConfigError,
    OAuth2CacheException,
    OAuth2TokenExpiredError
)

__all__ = (
    "CoaClientBaseException",
    "OAuth2ClientException",
    "OAuth2ConfigError",
    "OAuth2CacheException",
    "OAuth2TokenExpiredError",
    "CoaClientCommandException",
)
