# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import time
from azureml.core import Datastore


class _CachedItem:
    """CachedItem.
    :param value: The instance of cached object
    :type value: obj
    """

    def __init__(self, item, expired_time_in_seconds=60):
        self.item = item
        self.expired_time_in_seconds = expired_time_in_seconds
        self.cache_time = time.time()

    def is_expired(self):
        return time.time() - self.cache_time > self.expired_time_in_seconds


class _GeneralCache:
    """General cache for internal use."""
    _cache_dict = {}

    @classmethod
    def set_item(cls, key, item, expired_time_in_seconds=60):
        cls._cache_dict[key] = _CachedItem(item, expired_time_in_seconds)

    @classmethod
    def get_item(cls, key):
        cached = cls._cache_dict.get(key, None)

        if cached is None:
            return None

        if cached.is_expired():
            del cls._cache_dict[key]
            return None
        else:
            return cached

    @classmethod
    def delete_item(cls, key):
        if key in cls._cache_dict:
            del cls._cache_dict[key]


class DatastoreCache:
    """Datastore cache for internal use."""
    datastore_cache_expires_in_seconds = 3600
    # for None item, we only cache it for 1 minute
    datastore_cache_expires_in_seconds_for_none = 60

    @classmethod
    def _cache_key(cls, workspace, datastore_name):
        return 'datastore_{}_{}'.format(workspace._workspace_id, datastore_name)

    @classmethod
    def set_item(cls, workspace, datastore, datastore_name, expired_time_in_seconds=None):
        cache_key = cls._cache_key(workspace, datastore_name)
        if expired_time_in_seconds is None:
            if datastore is None:
                expired_time_in_seconds = cls.datastore_cache_expires_in_seconds_for_none
            else:
                expired_time_in_seconds = cls.datastore_cache_expires_in_seconds
        _GeneralCache.set_item(cache_key, datastore, expired_time_in_seconds)

    @classmethod
    def get_item(cls, workspace, datastore_name):
        cache_key = cls._cache_key(workspace, datastore_name)
        cached_item = _GeneralCache.get_item(cache_key)
        if cached_item is None:
            try:
                datastore = Datastore(workspace, datastore_name)
            except Exception:
                datastore = None
            cls.set_item(workspace, datastore, datastore_name)
            return datastore
        else:
            return cached_item.item


class ComputeTargetCache:
    """Compute target cache for internal use."""
    compute_cache_expires_in_seconds = 3600
    # for None item, we only cache it for 1 minute
    compute_cache_expires_in_seconds_for_none = 60

    @classmethod
    def _cache_key(cls, workspace, compute_name):
        return 'compute_{}_{}'.format(workspace._workspace_id, compute_name)

    @classmethod
    def set_item(cls, workspace, compute, compute_name, expired_time_in_seconds=None):
        cache_key = cls._cache_key(workspace, compute_name)
        if expired_time_in_seconds is None:
            if compute_name is None:
                expired_time_in_seconds = cls.compute_cache_expires_in_seconds_for_none
            else:
                expired_time_in_seconds = cls.compute_cache_expires_in_seconds
        _GeneralCache.set_item(cache_key, compute, expired_time_in_seconds)

    @classmethod
    def get_item(cls, workspace, compute_name):
        cache_key = cls._cache_key(workspace, compute_name)
        return _GeneralCache.get_item(cache_key)

    @classmethod
    def delete_item(cls, workspace, compute_name):
        cache_key = cls._cache_key(workspace, compute_name)
        _GeneralCache.delete_item(cache_key)

    @classmethod
    def get_cached_item_count(cls, workspace):
        prefix = cls._cache_key(workspace, '')
        return len([key for key in _GeneralCache._cache_dict.keys() if key.startswith(prefix)])
