import os
import logging

from .settings import settings


logger = logging.getLogger()
logger.setLevel(os.environ.get("CLS_LOG_LEVEL", "INFO"))

if not logger.hasHandlers():
    # AWS sets a handler automatically, so this helps local
    logger.addHandler(logging.StreamHandler())

if settings.is_debug():
    logger.setLevel(logging.DEBUG)
else:
    logger.disabled = True
