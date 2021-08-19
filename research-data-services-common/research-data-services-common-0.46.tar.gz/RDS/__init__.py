from .User import *
from .Service import *
from . import ServiceException
from .Token import *
from .Informations import *
from .ROParser import *
import RDS.Util as Util


def int_or_str(value):
    try:
        return int(value)
    except TypeError:
        return value


__version__ = "0.46"
VERSION = tuple(map(int_or_str, __version__.split(".")))

__all__ = [
    "User",
    "BaseService"
    "LoginService",
    "OAuth2Service",
    "LoginToken",
    "OAuth2Token",
    "Util",
    "ServiceException",
    "LoginMode",
    "FileTransferMode",
    "FileTransferArchive"
]
