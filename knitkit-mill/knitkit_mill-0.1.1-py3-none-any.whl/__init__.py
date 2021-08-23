try:
    from knitkit_mill.version import version as __version__
except ImportError:
    __version__ = "unknown"

from knitkit_mill import main
mill_source = main.mill_source
cache_source = main.cache_source
