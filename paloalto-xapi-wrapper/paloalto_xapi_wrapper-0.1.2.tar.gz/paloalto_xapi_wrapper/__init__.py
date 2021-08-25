try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)


from .xapi_wrapper import xapi_con
from .xapi_wrapper import xapi_set
from .xapi_wrapper import xapi_op
from .xapi_wrapper import xapi_commit