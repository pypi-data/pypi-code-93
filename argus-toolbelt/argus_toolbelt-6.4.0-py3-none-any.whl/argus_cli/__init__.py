try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

__version__ = version("argus-toolbelt")

from .plugin import register_command, register_provider, run
