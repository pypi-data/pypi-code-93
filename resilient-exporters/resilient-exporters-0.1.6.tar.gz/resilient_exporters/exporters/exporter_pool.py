import pathlib
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Union, Optional, List, Iterable, Text, Any
from resilient_exporters.exporters import Exporter, ExportResult
from resilient_exporters.exceptions import InvalidConfigError
from resilient_exporters.utils import is_able_to_connect

logger = logging.getLogger(__name__)


class ExporterPool(Exporter):
    """Enables pooling of exporters for improved efficiency and performance.
    All the exporters will be managed by the pool, including the saving of
    unsent data, with only one ``send`` call to be used. It also offers a
    multithreading option to run the exporters' ``send`` functions in parallel,
    to speed up the execution of ``ExporterPool.send``.

    Args:
        exporters (Iterable[Exporter]): a list of
            ``resilient_exporters.exporters.Exporter``.
        transform (Callable): a function to be invoked at each ``send`` call on
            the passed data. It must return data or exceptions will be raised.
        num_threads (int): the number of threads to use for ``send`` calls.
            Must be greater than 1. If 1, multithreading is disabled.
            Default to 1.
        wait_for_result (bool): value to decide if the instance has to wait for
            the result of ``send`` calls or not when multithreading is enabled.
        manual_reexport (bool): if True, the user is responsible to call the
            function ``send_unsent_data`` when appropriate. If False, the
            instance will manage that automatically by assessing the necessity
            to call the function at each ``send`` call; the criterias are 1)
            there's unsent data, 2) there's an Internet connection. Default to
            False.

    .. admonition:: Note

        If using parallelism, the default behaviour is to wait for the results
        of all calls. One can disable this behaviour with `wait_for_result` set
        to ``False``, and ``ExporterPool.send`` will be then non-blocking, but
        will return ``None``.

    Raises:
        InvalidConfigError: if ``num_threads`` is < 1.

    .. admonition:: Example

        .. code-block:: python

            import resilient_exporters as rex

            exporter1 = rex.exporters.FileExporter("local_file.txt")
            exporter2 = rex.exporters.FileExporter("/path/to/network/file.txt")
            pool = ExporterPool([exporter1, exporter2], num_threads=2)

            line = "A string to be written in a file"
            pool.send(line)

    Attributes:
        num_threads (int): number of threads used by the instance.
        wait_for_result (bool): value to decide if the instance has to wait for
            the results of ``send`` calls or not when multithreading is enabled
    """
    __futures = []
    __instantiated = 0

    def __init__(self,
                 exporters: Optional[Iterable[Exporter]],
                 transform: Optional[Callable] = None,
                 num_threads: int = 1,
                 wait_for_result: bool = True,
                 use_memory: bool = True,
                 manual_reexport: bool = False,
                 *,
                 tmp_file: Union[Text, pathlib.Path, None] = None,
                 save_unsent_data: bool = True):
        # @TODO: name: Optional[Text] = None
        super(ExporterPool, self).__init__(transform=transform,
                                           use_memory=use_memory,
                                           tmp_file=tmp_file,
                                           manual_reexport=manual_reexport,
                                           save_unsent_data=save_unsent_data)
        if num_threads < 1:
            raise InvalidConfigError(self, "num_threads must be >= 1; use \
                                    num_threads=1 to disable multithreading.")

        self.num_threads = num_threads
        self.wait_for_result = wait_for_result

        self.__exporters = {}
        if exporters is not None:
            for exporter in exporters:
                exporter._replace_datastore(self._datastore)
                if self._run_transform:
                    exporter._run_transform = False
                exporter._save_unsent_data = not self._save_unsent_data
                self.__exporters[exporter.name] = exporter

        self.__instantiated += 1
        self.name = f"exporterpool_{ExporterPool.__instantiated}"

    @property
    def exporters(self) -> dict:
        """A dictionary of the contained exporters."""
        return self.__exporters

    def add_exporter(self, exporter: Exporter) -> None:
        """Adds an exporter to the pool. Use this function to add an exporter
        after the pool has been initialised. It removes the responsability to
        run the `transform` method from the exporter, and to save unsent data.

        Args:
            exporter (Exporter): an exporter.
        """
        exporter.use_memory = self.use_memory
        if self._run_transform:
            exporter._run_transform = False
        exporter._save_unsent_data = not self.save_unsent_data
        self.__exporters[exporter.name] = exporter

    def send(self, data: Any, **kwargs) -> List[ExportResult]:
        """Runs the `send` method of all its exporters. If the pool's
        `num_threads` attribute is > 1, it will execute all the calls in
        separate threads.

        .. admonition:: Note
            The key arguments passed at the call of the method will be passed
            down to all the exporters. Make sure they all have different
            keywords.

        Args:
            data (Any): the data to export.
            **kwargs (Any): the keyword arguments to pass down to the
                exporters' `send` methods.

        Returns:
            List[ExportResult]: a list of the exporters' results.
        """
        results = []
        if self.num_threads <= 1:
            for exporter in self:
                results.append(exporter.send(data, **kwargs))
        else:
            # use multithreading
            futures = []
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                for exporter in self:
                    future = executor.submit(exporter.send, data, **kwargs)
                    futures.append(future)

                    def save_if_failed(future):
                        if not future.result():
                            self.save_unsent_data(data, kwargs, exporter.name)

                    future.add_done_callback(save_if_failed)
            if self.wait_for_result:
                results += [f.result() for f in futures]
            else:
                self.__futures += futures
        return results

    def _process_result(self,
                        results: Iterable[ExportResult],
                        data: Any,
                        kwargs: dict) -> Union[bool, List[bool]]:
        summed_res = sum([r.successful for r in results])
        if summed_res == len(results):
            # all expeditions have been successful
            if not self.manual_reexport \
               and is_able_to_connect(self.TEST_URL) \
               and self.has_unsent_data():
                logger.info("Attempt to send previously unsent data.")
                return results + self.send_unsent_data()
        elif summed_res == 0 and self._save_unsent_data:
            # all have failed
            self.save_unsent_data(data, kwargs, self.name)
        else:
            # mixed results
            for exporter, res in zip(self, results):
                if not res.successful and self._save_unsent_data:
                    self.save_unsent_data(data, kwargs, exporter.name)
        return results

    def send_unsent_data(self) -> List[ExportResult]:
        """Tries to send the previously saved, unsent data.

        Returns:
            List[ExportResult]: list of the results of the export jobs.
        """
        self.__is_sending_unsent_data = True
        results = [self.send(d["data"], d["exporter"], **d["kwargs"])
                   for d in self._datastore]
        self.__is_sending_unsent_data = False
        return results

    def __len__(self) -> int:
        return len(self.__exporters)

    def __iter__(self):
        self.__iterator_count = 0
        self.__exporters_as_list = list(self.exporters.values())
        return self

    def __next__(self) -> Optional[Exporter]:
        if self.__iterator_count < len(self):
            res = self.__exporters_as_list[self.__iterator_count]
            self.__iterator_count += 1
            return res
        del self.__exporters_as_list
        raise StopIteration

    def __del__(self):
        if not self.wait_for_result:
            _ = [f.result() for f in self.__futures]
            del _
            del self.__futures
