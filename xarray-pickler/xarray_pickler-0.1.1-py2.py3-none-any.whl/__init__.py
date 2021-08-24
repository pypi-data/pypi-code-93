"""Top-level package for xarray-pickler."""

__author__ = """Elle Smith"""
__contact__ = "eleanor.smith@stfc.ac.uk"
__copyright__ = "Copyright 2020 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"

import logging.config
import os

import xarray_pickler
from xarray_pickler.config import get_config

CONFIG = get_config()

logging.config.fileConfig(
    os.path.join(os.path.dirname(__file__), "etc", "logging.conf"),
    disable_existing_loggers=False,
)

from xarray_pickler.xarray_pickler import open_dset
