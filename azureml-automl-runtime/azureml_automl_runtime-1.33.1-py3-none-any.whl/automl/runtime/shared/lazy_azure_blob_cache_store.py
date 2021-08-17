# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module containing the implementation for an azure based cache to be used for saving automl data between runs."""
from typing import Any, Dict, Iterable, List, Optional
import io
import logging
import os
import shutil
import tempfile

import numpy as np
from scipy import sparse

from azureml._vendor.azure_storage.blob.models import Blob
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import CacheException
from azureml.automl.runtime.shared import lazy_file_cache_store as lfcs
from azureml.data.azure_storage_datastore import AzureBlobDatastore

logger = logging.getLogger()


class LazyAzureBlobCacheStore(lfcs.LazyFileCacheStore):
    """File cache store backed by azure blob."""
    def __init__(
        self,
        data_store: AzureBlobDatastore,
        blob_path: str,
        task_timeout: int = lfcs._CacheConstants.DEFAULT_TASK_TIMEOUT_SECONDS
    ):
        super().__init__(tempfile.mkdtemp())

        self._data_store = data_store
        self._blob_path = blob_path + "/cache"
        self._task_timeout = task_timeout
        self._validate_data_store()

    def _validate_data_store(self) -> None:
        """
        Validate datastore object and it's various attributes.
        """
        Contract.assert_value(value=self._data_store, name='data_store', log_safe=True)
        Contract.assert_value(value=self._data_store.blob_service, name='data_store.blob_service', log_safe=True)
        Contract.assert_value(value=self._data_store.container_name, name='data_store.container_name', log_safe=True)

    def _list_files(self) -> List[Blob]:
        """
        List files available in the data store.

        :return: List of files in the data store.
        """
        blob_service = self._data_store.blob_service
        files = list(blob_service.list_blobs(container_name=self._data_store.container_name,
                                             prefix=self._blob_path))
        logger.debug('Number of files in the blob store: {}'.format(len(files)))
        return files

    def load(self) -> None:
        """
        Read the contents of the blob at the path and store keys, data references to them
        in memory. This will hydrate `cached_items` field of this.
        """
        try:
            with self.log_activity():
                blobs = self._list_files()
        except Exception as ex:
            logging_utilities.log_traceback(ex, logger, is_critical=False)
            msg = "Failed to list blobs in the datastore"
            raise CacheException.from_exception(ex, msg=msg).with_generic_msg(msg)

        for blob in blobs:
            blob_name = blob.name
            cached_file_name = blob_name.split("/")[-1]
            cache_key, ext = self._split_file_ext(cached_file_name)

            if ext == lfcs._CacheConstants.NUMPY_FILE_EXTENSION:
                func = np.load
            elif ext == lfcs._CacheConstants.SCIPY_SPARSE_FILE_EXTENSION:
                func = sparse.load_npz
            else:
                func = self._pickler.load

            self.cache_items[cache_key] = lfcs.CachedValue(blob_name, func)

    def get(self, keys: Iterable[str], default: Optional[Any] = None) -> Dict[str, Any]:
        """
        Get deserialized object from store.

        :param keys: Keys to retrieve the values for.
        :param default: returns default value if not present
        :return: deserialized objects
        """
        Contract.assert_value(value=keys, name='keys', log_safe=True)
        res = {}
        with self.log_activity():
            for key in keys:
                item = self.cache_items.get(key)
                try:
                    if item is not None:
                        in_stream = io.BytesIO()
                        self._data_store.blob_service.get_blob_to_stream(
                            self._data_store.container_name,
                            item.path,
                            in_stream
                        )
                        temp_file = tempfile.NamedTemporaryFile(delete=False)
                        temp_file.write(in_stream.getvalue())
                        temp_file.close()
                        res[key] = item.func(temp_file.name)
                        os.remove(temp_file.name)
                    else:
                        res[key] = default
                except MemoryError:
                    raise
                except Exception as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    msg = "Failed to retrieve {1} from cache. Exception type: {0}".format(
                        e.__class__.__name__,
                        key)
                    logger.warning(msg)
                    res[key] = default

        return res

    def set(self, key: str, value: Any) -> None:
        """
        Set key and value in the cache.

        :param key: Key to store.
        :param value: Value to store.
        """
        Contract.assert_value(value=key, name='key', log_safe=True)
        self.add([key], [value])

    def add(self, keys: Iterable[str], values: Iterable[Any]) -> None:
        """
        Serialize the values and add them to cache and upload to the azure blob container.

        :param keys: List of keys.
        :param values: Corresponding values to be cached.
        """
        Contract.assert_value(value=keys, name='keys', log_safe=True)
        with self.log_activity():
            try:
                # Write the value temporarily to disk and store refs as
                # CachedValue in self.cache_items.
                # The `path` of the CachedValues is temporary local disk path.
                for key, value in zip(keys, values):
                    self._write(key, value)

                # Upload temp files to blob and return CachedValues with
                # path updated to the uploaded Blob store path.
                uploaded_items = self._upload_multiple([self.cache_items[key] for key in keys])

                # Set the CachedValues back to the index.
                for idx, key in enumerate(keys):
                    self.cache_items[key] = uploaded_items[idx]
            except MemoryError:
                raise
            except Exception as ex:
                logging_utilities.log_traceback(ex, logger, is_critical=False)
                msg = "Failed to add to cache. Exception type: {0}".format(ex.__class__.__name__)
                raise CacheException.from_exception(ex, msg=msg).with_generic_msg(msg)

    def remove(self, key: str) -> None:
        """
        Remove key from store.

        :param key: store key
        """
        try:
            to_remove = self.cache_items[key]
            self._data_store.blob_service.delete_blob(
                self._data_store.container_name,
                to_remove.path,
                timeout=self._task_timeout
            )
            del self.cache_items[key]
        except KeyError as ke:
            logging_utilities.log_traceback(ke, logger, is_critical=False)
            msg = "Failed to find key '{}' in cache.".format(key)
            raise CacheException.from_exception(ke, msg=msg).with_generic_msg(msg)
        except Exception as e:
            logging_utilities.log_traceback(e, logger, is_critical=False)
            msg = "Failed to delete key '{}' from cache. Exception type: {}".format(
                key, e.__class__.__name__)
            raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

    def remove_all(self):
        """Remove all the cache from store."""
        keys = list(self.cache_items.keys())
        for key in keys:
            self.remove(key)

    def upload_file(self, src: str, dest: str) -> None:
        """
        Upload a file directly to AzureML Datastore specifing target_path via dest.

        :param src: The full path to the disired fill to upload.
            NOTE - src can be based of grain key/value combinations and should not be logged!
        :type src: str
        :param dest: The target_path to be written to within the Datastore (backed by Azure Blob).
        :type dest: str
        """
        with self.log_activity():
            try:
                self._data_store.upload_files(
                    files=[src],
                    target_path=dest,
                    show_progress=False,
                    overwrite=True
                )
            except MemoryError:
                raise
            except Exception as e:
                logging_utilities.log_traceback(e, logger, is_critical=False)
                msg = "Failed to upload file to the cache. Exception type: {}".format(
                    e.__class__.__name__
                )
                raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

    def _upload(self, cached_value: lfcs.CachedValue) -> lfcs.CachedValue:
        """
        Upload a single file represented by cached_value to the blob store.

        :param cached_value: The item to be uploaded.
        :returns: An updated CachedValue with the path pointing to the location of file on blob.
        """
        return self._upload_multiple([cached_value])[0]

    def _upload_multiple(
            self,
            cached_values: List[lfcs.CachedValue]) -> List[lfcs.CachedValue]:
        """
        Upload multiple files represented by cached_values to the blob store.

        :param cached_values: The items to be uploaded.
            NOTE cached_value file paths may not be log safe!
        :returns: Updated CachedValue list with the path pointing to the location of files on blob.
        """
        with self.log_activity():
            files = [c.path for c in cached_values]
            file_names = [os.path.split(file_path)[1] for file_path in files]
            upload_path = self._blob_path
            try:
                self._data_store.upload_files(
                    files=files,
                    target_path=upload_path,
                    show_progress=False,
                    overwrite=True
                )
            except MemoryError:
                raise
            except Exception as e:
                logging_utilities.log_traceback(e, logger, is_critical=False)
                msg = "Failed to upload files to the cache. Exception type: {}".format(
                    e.__class__.__name__
                )
                raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

            return [lfcs.CachedValue(
                '{upload_path}/{file_name}'.format(upload_path=upload_path, file_name=file_name),
                c.func
            ) for file_name, c in zip(file_names, cached_values)]

    def __repr__(self):
        path = self._blob_path[:self._blob_path.rfind("/cache")]
        return "{c}(data_store=\"{ds}\", blob_path=\"{path}\", task_timeout={to})".format(
            c=self.__class__.__name__, ds=self._data_store, path=path, to=self._task_timeout)

    def __del__(self):
        shutil.rmtree(self._root)

    def __getstate__(self):
        """
        Get this cache store's state.

        :return: a dict containing serializable state.
        """
        return super().__getstate__(), {
            'blob_path': self._blob_path,
            'max_retries': self.max_retries,
            'task_timeout': self._task_timeout,
            'ds_name': self._data_store.name,
            'ds_account_name': self._data_store.account_name,
            'ds_account_key': self._data_store.account_key,
            'ds_container_name': self._data_store.container_name,
            'ds_protocol': self._data_store.protocol,
            'ds_sas_token': self._data_store.sas_token
        }

    def __setstate__(self, state):
        """
        Deserialize this cache store's state.

        :param state: dictionary containing object state
        """
        super_state, my_state = state
        ds_name = my_state['ds_name']
        ds_account_name = my_state['ds_account_name']
        ds_account_key = my_state['ds_account_key']
        ds_container_name = my_state['ds_container_name']
        ds_protocol = my_state['ds_protocol']
        ds_sas_token = my_state['ds_sas_token']

        self._data_store = AzureBlobDatastore(
            workspace=None,
            name=ds_name,
            container_name=ds_container_name,
            account_name=ds_account_name,
            account_key=ds_account_key,
            sas_token=ds_sas_token,
            protocol=ds_protocol
        )

        self._blob_path = my_state['blob_path']
        self._task_timeout = my_state['task_timeout']
        self.max_retries = my_state['max_retries']
        super().__setstate__(super_state)
