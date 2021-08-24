__title__ = 'Laminos.py'
__author__ = 'Legion'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020-2021 Slimakoi, Legion_refix'
__version__ = '1.2.17.1'

from .client import Client
from .sub_client import SubClient
from .socket import Callbacks, SocketHandler
from .lib.util import device, exceptions, headers, helpers, objects, acm
from requests import get
from json import loads

__newest__ = loads(get("https://pypi.python.org/pypi/Amino.py/json").text)["info"]["version"]

if __version__ != __newest__:
    print(exceptions.LibraryUpdateAvailable(f"New version of {__title__} available: {__newest__} (Using {__version__})"))