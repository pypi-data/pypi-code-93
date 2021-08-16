"""
Coursera OAuth2.0 client library
"""

from .client import build
from .config import Config

__all__ = (
    "build",
    "Config",
)
