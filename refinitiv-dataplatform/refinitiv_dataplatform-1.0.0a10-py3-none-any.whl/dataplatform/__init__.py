# coding: utf-8
__version__ = "1.0.0a10"

"""
    refinitiv-dataplatform is a Python library to access Refinitiv Data Platform with Python.
"""

from .errors import *
from .core import *  # noqa
from .content import *  # noqa
from .delivery import *  # noqa
from .factory import *  # noqa
from .pricing import *  # noqa
from .content import ipa  # noqa
from .legacy.tools import get_default_session, close_session  # noqa
from . import log
from .content import historical_pricing, esg

del get_chain_async
del get_headlines
del get_headlines_async
del get_story
del get_story_async
del News
del State
del Lock

import sys

logger = log.root_logger
logger.debug(f"RDP version is {__version__}; Python version is {sys.version}")

try:
    import pkg_resources

    installed_packages = pkg_resources.working_set
    installed_packages = sorted([f"{i.key}=={i.version}" for i in installed_packages])
    logger.debug(
        f"Installed packages ({len(installed_packages)}): {','.join(installed_packages)}"
    )
except Exception as e:
    logger.debug(f"Cannot log installed packages, {e}")

from . import configure

logger.debug(f'Read configs: {", ".join(configure._config_files_paths)}')
