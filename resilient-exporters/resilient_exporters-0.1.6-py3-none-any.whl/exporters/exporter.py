import abc
import pathlib
import logging
import time
from collections import namedtuple
from collections.abc import MutableSequence, Set
from functools import wraps
from typing import Callable, Union, Optional, List, Text, Any
from ..utils import is_able_to_connect, _DataStore

logger = logging.getLogger(__name__)

ExportResult = namedtuple("ExportResult", ["returned", "successful"])


class Exporter(metaclass=abc.ABCMeta):
    """Base class of all exporters and ExporterPool. It includes a non-
    implemented `send` function that its children must implement. It has
    `abc.ABCMeta` as a metaclass to enforce the implementation of `send` by all
    the children classes.
    """

    TEST_URL: Optional[Text] = None
    """The URL to use to test a connection. If None, the URL will be
       "https://www.google.com".
    """

    __initialized: bool = False
    __instantiated: int = 0

    def __init__(self,
                 transform: Optional[Callable] = None,
                 timeout: int = 30,  # in seconds
                 use_memory: bool = True,
                 manual_reexport: bool = True,
                 *,
                 tmp_file: Union[Text, pathlib.Path, None] = None,
                 # @TODO: reinitialize_tmp_file: bool = True,
                 save_unsent_data: bool = True,
                 # @TODO: name: Optional[Text] = None,
                 test_url: Optional[Text] = None):
        if timeout < 0:
            raise ValueError("timeout must be non-negative and non null")

        self.__transform = transform
        self.timeout = timeout
        self.manual_reexport = manual_reexport
        self.TEST_URL = test_url

        self.tmp_filename = tmp_file
        self.name = f"exporter_{Exporter.__instantiated}"
        self._run_transform = transform is not None
        self._save_unsent_data = save_unsent_data

        self._only_stop_if_all_data_sent = False
        self._datastore = _DataStore(use_memory=use_memory,
                                     shelf_filename=self.tmp_filename)
        self.__approx_qsize = 0
        self.__initialized = True
        Exporter.__instantiated += 1
        self.__is_sending_unsent_data = False

        # If __init__ is called by an exporter that implements the `send`
        # method which means the type of self must be != "Exporter",
        # e.g. "FileExporter".
        # We wrap the `send` method to include pre- and post- processes.
        if type(self).__name__ != "Exporter":
            self.send = self._exporter_wrapper(self.send)
        logger.debug(f"Exporter {self.name} instantiated.")

    @property
    def use_memory(self) -> bool:
        """The value `use_memory` of the instance.

        When set to ``True``, it loads the data into memory if
        it was previously using a file (previous value was
        ``False``), or vice versa.

        Args:
            new_val (bool): new value for `use_memory`.

        Returns:
            bool: its value
        """
        return self._datastore.use_memory

    @use_memory.setter
    def use_memory(self, new_val: bool) -> bool:
        self._datastore.use_memory = new_val
        return new_val

    # @TODO: getter for transform
    # @property
    # def transform(self) -> Optional[Callable]:
    #    """Getter for `transform`. It has no corresponding setter. `transform`
    #    cannot be changed after instanciation to avoid corrupting previously
    #    transformed data.
    #
    #    Returns:
    #        Optional[Callable]: the `transform` function or `None` if none has
    #        been provided at initialisation.
    #    """
    #    return self.__transform

    def transform(self, data: Any) -> Any:
        """Applies `transform` to the given data.

        Args:
            data (Any): the data to pass to `transform`.

        Returns:
            Any: the output of `transform`

        Raises:
            Exception: if the output of `transform(data)` is None.
        """
        if self.__transform is None:
            return data
        logger.debug(f"transform input data of type {type(data)}")
        data = self.__transform(data.copy())
        if data is None:
            raise Exception("Empty data returned by transform.")
        logger.debug(f"transform output data of type {type(data)}")
        return data

    def save_unsent_data(self,
                         data: Any,
                         kwargs: dict,
                         exporter_name: str) -> None:
        """Saves the data in memory or disk, depending on the value of
        `use_memory` of the instance, so it can be sent later.

        Args:
            data (Any): the core data.
            kwargs (dict): the keyword arguments to pass to `send` for
                           the given data.
            exporter_name (str): the name of the exporter.

        Returns:
            None
        """
        data_to_keep = {"data": data,
                        "kwargs": kwargs,
                        "exporter": exporter_name}
        self._datastore.put(data_to_keep)

    def has_unsent_data(self) -> bool:
        """Assesses if there's saved, unsent data.

        Returns:
            bool: `True` if there's saved, unsent data. `False` otherwise.
        """
        return self._datastore.size > 0

    def _exporter_wrapper(self, send_func: Callable) -> Callable:
        """Wrapper for the implemented ``send`` method. It checks data type,
        runs the call ``transform`` on the data, and processes the result.

        Args:
            send_func (Callable): an implementation of ``Exporter.send``

        Returns:
            Callable: the wrapped ``send`` method.
        """

        @wraps(send_func)
        def wrapper(data: Any, *args, **kwargs) -> Union[ExportResult,
                                                         List[ExportResult]]:
            logger.debug(f"Sending input data of type {type(data)}")
            if data is None:
                raise ValueError("No data.")
            if isinstance(data, MutableSequence):
                raise ValueError("Data cannot be a list or a MutableSequence")
            if isinstance(data, Set):
                raise ValueError("Data cannot be a tuple or a Set")
            if self._run_transform:
                data = self.transform(data)
            logger.debug(f"Calling `send` of exporter {self.name}")
            result = send_func(data, **kwargs)
            logger.debug(f"Processing result {result}")
            return self._process_result(result, data, kwargs)
        return wrapper

    def send_unsent_data(self) -> List[ExportResult]:
        """Tries to send the previously saved, unsent data.

        Returns:
            List[ExportResult]: list of the results of the export jobs.
        """
        self.__is_sending_unsent_data = True
        results = [self.send(d["data"], **d["kwargs"])
                   for d in self._datastore]
        self.__is_sending_unsent_data = False
        return results

    @abc.abstractmethod
    def send(self, data, **kwargs) -> Union[ExportResult, List[ExportResult]]:
        """Abstract method to be implemented by children.

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    def _process_result(self,
                        result: ExportResult,
                        data: Any,
                        kwargs: dict) -> Union[ExportResult,
                                               List[ExportResult]]:
        if result.successful:
            if not self.manual_reexport \
               and is_able_to_connect(self.TEST_URL)\
               and self.has_unsent_data():
                logger.info("Attempt to send previously unsent data.")
                return [result] + self.send_unsent_data()
        elif not result.successful and self._save_unsent_data:
            self.save_unsent_data(data, kwargs, self.name)
        return result

    def _replace_datastore(self, new_datastore: _DataStore):
        self._datastore = new_datastore

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'send') and
                callable(subclass.send) and
                hasattr(subclass, 'has_unsent_data') and
                callable(subclass.has_unsent_data))

    def __setattr__(self, attr, val):
        if self.__initialized and attr in ('transform', 'tmp_file'):
            raise ValueError(f'{attr} attribute should not be set after '
                             f'{self.__class__.__name__} is initialized.')
        super(Exporter, self).__setattr__(attr, val)

    def __del__(self):
        if self._only_stop_if_all_data_sent and self.has_unsent_data():
            while self.has_unsent_data():
                self.send_unsent_data()
                time.sleep(0.2)
        del self
