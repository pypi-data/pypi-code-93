# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Factory class that automatically selects the appropriate cache store."""
import logging
from typing import Optional

from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.automl.runtime.shared.file_cache_store import FileCacheStore, _CacheConstants
from azureml.automl.runtime.shared.memory_cache_store import MemoryCacheStore
from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore, AzureBlobDatastore
from azureml.automl.runtime.shared.lazy_azure_blob_cache_store import LazyAzureBlobCacheStore

logger = logging.getLogger(__name__)


class CacheStoreFactory:

    @staticmethod
    def get_cache_store(temp_location: str,
                        run_target: str,
                        run_id: Optional[str],
                        data_store: Optional[AzureBlobDatastore] = None,
                        task_timeout: int = _CacheConstants.DEFAULT_TASK_TIMEOUT_SECONDS) -> CacheStore:
        """Get the cache store based on run type."""
        try:
            if run_id is None:
                return MemoryCacheStore()

            if data_store is not None and run_target != "local":
                Contract.assert_type(data_store, name='data_store', expected_types=AzureBlobDatastore)

                return LazyAzureBlobCacheStore(
                    data_store=data_store, blob_path=run_id, task_timeout=task_timeout
                )

            return FileCacheStore(path=temp_location, task_timeout=task_timeout)
        except Exception as e:
            logger.warning("Cannot proceed with the Run {} without a valid storage for intermediate files. "
                           "Encountered an exception of type: {}".format(run_id, type(e)))
            raise
