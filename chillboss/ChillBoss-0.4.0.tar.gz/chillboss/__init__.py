"""ChillBoss package."""

from importlib_metadata import version

from chillboss import loggers
from chillboss.mouse import Pointer

__version__ = version("chillboss")

__all__ = ["Pointer", "__version__"]
