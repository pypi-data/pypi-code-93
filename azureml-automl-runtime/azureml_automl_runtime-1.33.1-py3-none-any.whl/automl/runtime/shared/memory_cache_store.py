# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Memory-based cache store."""
import copy

from .cache_store import CacheStore


class MemoryCacheStore(CacheStore):
    """MemoryCacheStore - stores value in memory."""

    def load(self):
        """Load from memory - NoOp."""
        pass

    def add(self, keys, values):
        """
        Add to store by creating a deep copy.

        :param keys: store key
        :param values: store value
        """
        for k, v in zip(keys, values):
            self.cache_items[k] = copy.deepcopy(v)

    def unload(self):
        """Unload from memory."""
        self.cache_items.clear()
