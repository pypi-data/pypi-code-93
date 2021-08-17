# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""File-based cache store."""
import errno
from enum import Enum
from typing import Any, Dict, Iterable, Optional
import logging
import numpy as np
import os
import sys  # noqa F401 # dynamically evaluated to get caller
import tempfile

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import CacheOperation, MissingCacheContents
from scipy import sparse

from .cache_store import CacheStore
from azureml.automl.core.shared.pickler import DefaultPickler
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import CacheException


logger = logging.getLogger(__name__)


class _SavedAsProtocol(Enum):
    PICKLE = 1
    NUMPY = 2
    SCIPY = 3


class _CacheConstants:
    # default task timeout
    DEFAULT_TASK_TIMEOUT_SECONDS = 900

    # Extension name for files that are saved by Numpy.save()
    NUMPY_FILE_EXTENSION = 'npy'

    # Extension name for files that are saved by SciPy.save()
    SCIPY_SPARSE_FILE_EXTENSION = 'npz'

    # File name for metadata file (which stores mapping of what was stored and in what format)
    SAVED_AS_FILE_NAME = 'saved_as'


class FileCacheStore(CacheStore):
    """FileCacheStore - cache store based on file system."""
    _pickler = DefaultPickler()

    def __init__(self,
                 path: str,
                 task_timeout: int = _CacheConstants.DEFAULT_TASK_TIMEOUT_SECONDS):
        """
        File based cache store - constructor.

        :param path: store path
        :param task_timeout: task timeout
        """
        super(FileCacheStore, self).__init__()

        self.task_timeout = task_timeout
        self.path = _create_temp_dir(path)
        self.saved_as = dict()  # type: Dict[str, _SavedAsProtocol]

    def __getstate__(self):
        """
        Get this cache store's state, removing unserializable objects in the process.

        :return: a dict containing serializable state.
        """
        return super().__getstate__(), {
            'path': self.path,
            'task_timeout': self.task_timeout,
            'saved_as': self.saved_as,
        }

    def __setstate__(self, state):
        """
        Deserialize this cache store's state, using the default logger.

        :param state: dictionary containing object state
        :type state: dict
        """
        super_state, my_state = state
        self.path = my_state['path']
        self.task_timeout = my_state['task_timeout']
        self.saved_as = my_state.get('saved_as') or dict()
        super().__setstate__(super_state)

    @property
    def _saved_as_file_path(self) -> str:
        return os.path.join(self.path, _CacheConstants.SAVED_AS_FILE_NAME)

    def add(self, keys: Iterable[str], values: Iterable[Any]) -> None:
        """
        Pickles the object and adds to cache.

        :param keys: store keys
        :param values: store values
        """
        with self.log_activity():
            for k, v in zip(keys, values):
                try:
                    logger.info("Uploading key: " + k)
                    self._upload(k, v)
                except OSError as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    logger.error("Failed to persist the keys [{}] to the local disk. Error code: {}".format(
                        ",".join(keys), e.errno))
                    raise CacheException._with_error(
                        AzureMLError.create(CacheOperation, target="cache-add", operation_name="add",
                                            path=self.path, os_error_details=str(e)),
                        inner_exception=e
                    ) from e
                except Exception as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    msg = "Failed to add key {} to cache. Exception type: {}".format(k, e.__class__.__name__)
                    raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

    def _deserialize(self, key: str, path: str) -> Any:
        saved_as = self.saved_as.get(key, None)
        if saved_as == _SavedAsProtocol.SCIPY:
            logger.debug('Downloading and de-serializing "{}" via. Scipy from cache'.format(key))
            deserialized_obj = sparse.load_npz(path)
        elif saved_as == _SavedAsProtocol.NUMPY:
            logger.debug('Downloading and de-serializing "{}" via. Numpy from cache'.format(key))
            deserialized_obj = np.load(path)
        elif saved_as == _SavedAsProtocol.PICKLE:
            logger.debug('Downloading and unpickling "{}" from cache'.format(key))
            deserialized_obj = self._pickler.load(path)
        else:
            raise CacheException(
                "Cannot determine serialization protocol for '{}' "
                "or the key was not present in the 'saved_as' file.".format(key), has_pii=False)
        return deserialized_obj

    def get(self, keys, default=None):
        """
        Get unpickled object from store.

        :param keys: store keys
        :param default: returns default value if not present
        :return: unpickled objects
        """
        res = dict()

        with self.log_activity():
            for key in keys:
                try:
                    path = self.cache_items.get(key, None)
                    obj = default
                    logger.info("Getting data for key: " + key)
                    if path is not None:
                        obj = self._deserialize(key, path)
                    res[key] = obj
                except OSError as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    logger.error("Failed to get the keys [{}] from the local cache on disk. Error code: {}".format(
                        ",".join(keys), e.errno))
                    raise CacheException._with_error(
                        AzureMLError.create(CacheOperation, target="cache-get", operation_name="get",
                                            path=self.path, os_error_details=str(e)),
                        inner_exception=e
                    ) from e
                except Exception as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    msg = "Failed to retrieve key {} from cache. Exception type: {}".format(
                        key, e.__class__.__name__)
                    raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

        return res

    def set(self, key, value):
        """
        Set to store.

        :param key: store key
        :param value: store value
        """
        self.add([key], [value])

    def remove(self, key):
        """
        Remove from store.

        :param key: store key
        """
        logger.info("Deleting data for key: " + key)
        with self.log_activity():
            try:
                self.cache_items.pop(key)
                os.remove(key)
            except OSError as e:
                err_msg = "Failed to remove {} from store".format(key)
                if e.errno != errno.ENOENT:
                    logger.error(err_msg)
                    raise
                else:
                    logger.warning(err_msg)
            except KeyError:
                logger.warning("Failed to remove {} from store".format(key))
            except Exception:
                logger.warning("Remove from store failed.")

    def remove_all(self):
        """Remove all the cache from store."""
        length = self.cache_items.__len__()
        logger.info("Removing all items from cache store.")
        with self.log_activity():
            while length > 0:
                length -= 1
                k, v = self.cache_items.popitem()
                try:
                    # For back compatibility (e.g. with continue_runs), if saved_as file is absent, delete the file
                    if not self.saved_as:
                        os.remove(v)
                    elif k in self.saved_as:
                        # Delete the file only if it was cached via the cache store (e.g. files saved outside the
                        # context of cache_store, such as outputs, shouldn't be removed
                        os.remove(v)
                except OSError as e:
                    logger.warning('Failed to remove {} from cache store'.format(v))
                    if e.errno != errno.ENOENT:
                        raise

    def load(self):
        """Load from store."""
        logger.info("Loading from file cache")
        with self.log_activity():
            self._try_loading_saved_as_object()
            for f in os.listdir(self.path):
                key = self._pickler.get_name_without_extn(f)
                val = os.path.join(self.path, f)
                self.cache_items[key] = val
            self._validate_saved_as_files_present()

    def unload(self):
        """Unload from store."""
        # load to make sure all the meta files are loaded
        self.load()

        logger.info("Unloading from file cache")
        self.remove_all()
        try:
            os.remove(self._saved_as_file_path)
        except OSError as e:
            logger.warning('Failed to remove the "saved_as" file')
            if e.errno != errno.ENOENT:
                raise
        _try_remove_dir(self.path)

    def _validate_saved_as_files_present(self):
        # validate that the saved_as files are actually present on disk
        diff = self.saved_as.keys() - self.cache_items.keys()
        if len(diff) > 0:
            logger.error("Cache store is missing previously cached keys: {}".format(diff))
            raise CacheException._with_error(AzureMLError.create(
                MissingCacheContents, target="cache-load", path=self.path, files=", ".join(diff))
            )

    def _try_loading_saved_as_object(self):
        logger.info("Loading the saved_as object from cache.")
        if os.path.exists(self._saved_as_file_path):
            self.saved_as = self._pickler.load(self._saved_as_file_path)
            logger.info("The saved_as object is: " + str(self.saved_as))

    def _persist_saved_as_file(self) -> None:
        self._pickler.dump(self.saved_as, self._saved_as_file_path)
        logger.info("The saved_as object is: " + str(self.saved_as))

    def _serialize_numpy_ndarray(self, file_name: str, obj: np.ndarray) -> Any:
        assert isinstance(obj, np.ndarray)
        logger.debug('Numpy saving and uploading "{}" to cache'.format(file_name))
        path = os.path.join(self.path, file_name)
        np.save(path, obj, allow_pickle=False)
        return path

    def _serialize_scipy_sparse_matrix(self, file_name: str, obj: Any) -> Any:
        assert sparse.issparse(obj)
        logger.debug('Scipy saving and uploading "{}" to cache'.format(file_name))
        path = os.path.join(self.path, file_name)
        sparse.save_npz(path, obj)
        return path

    def _serialize_object_as_pickle(self, file_name: str, obj: Any) -> Any:
        logger.debug('Pickling and uploading "{}" to cache'.format(file_name))
        path = os.path.join(self.path, file_name)
        self._pickler.dump(obj, path=path)
        return path

    def _serialize(self, file_name: str, obj: Any) -> Any:
        key_name = file_name
        if isinstance(obj, np.ndarray) and obj.dtype != np.object:
            key_name = '.'.join([file_name, _CacheConstants.NUMPY_FILE_EXTENSION])
            local_file_path = self._serialize_numpy_ndarray(key_name, obj)
            self.saved_as[file_name] = _SavedAsProtocol.NUMPY
        elif sparse.issparse(obj):
            key_name = '.'.join([file_name, _CacheConstants.SCIPY_SPARSE_FILE_EXTENSION])
            local_file_path = self._serialize_scipy_sparse_matrix(key_name, obj)
            self.saved_as[file_name] = _SavedAsProtocol.SCIPY
        else:
            local_file_path = self._serialize_object_as_pickle(key_name, obj)
            self.saved_as[file_name] = _SavedAsProtocol.PICKLE

        return local_file_path

    def _upload(self, key, obj):
        try:
            path = self._serialize(key, obj)
            self.cache_items[key] = path
            self._persist_saved_as_file()
            logger.info("Uploaded key: " + key)
        except Exception:
            logger.error("Uploading {} failed.".format(key))
            raise


def _create_temp_dir(temp_location: Optional[str]) -> str:
    """
    Create temp dir.

    :return: temp location
    """
    try:
        if temp_location is None:
            return tempfile.mkdtemp()
        cache_path = os.path.join(temp_location, 'cache')
        os.makedirs(cache_path, exist_ok=True)
        return tempfile.mkdtemp(dir=cache_path)
    except OSError as e:
        logging_utilities.log_traceback(e, logger, is_critical=False)
        logger.error("Failed to initialize the cache store. Error code: {}".format(e.errno))
        raise CacheException._with_error(AzureMLError.create(
            CacheOperation, target="cache-init", operation_name="initialization",
            path=temp_location, os_error_details=str(e)),
            inner_exception=e
        ) from e


def _try_remove_dir(path):
    """
    Remove directory.

    :param path: path to be removed
    """
    try:
        os.rmdir(path)
    except OSError:
        return False

    return True
