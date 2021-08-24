try:
    CRAFTAI_PANDAS_ENABLED = True
    from .. import errors, Time
    from .client import Client
    from .interpreter import Interpreter
    from .constants import MISSING_VALUE, OPTIONAL_VALUE
except ImportError:
    CRAFTAI_PANDAS_ENABLED = False
    errors = None
    Time = None
    Client = None
    Interpreter = None
    MISSING_VALUE = None
    OPTIONAL_VALUE = None

# Defining what will be imported when doing `from craft_ai.pandas import *`
__all__ = [
    "Client",
    "errors",
    "Interpreter",
    "Time",
    "MISSING_VALUE",
    "OPTIONAL_VALUE",
    "CRAFTAI_PANDAS_ENABLED",
]
