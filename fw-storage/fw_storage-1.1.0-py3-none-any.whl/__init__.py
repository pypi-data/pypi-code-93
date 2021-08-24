"""Flywheel storage library."""
import importlib.metadata as importlib_metadata

from .storage import FileNotFound, PermError, Storage, StorageError, get_storage

__all__ = ["FileNotFound", "PermError", "Storage", "StorageError", "get_storage"]
__version__ = importlib_metadata.version(__name__)
