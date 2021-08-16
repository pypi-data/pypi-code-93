import os
import orjson as json
import logging
import shutil
from typing import Optional, Text, Union, Iterable
from resilient_exporters.exporters import Exporter, ExportResult
from resilient_exporters.exceptions import ExportError

logger = logging.getLogger(__name__)


class FileExporter(Exporter):
    """Exporter for a text file.

    Args:
        target_file (str): the path of the file. The user must have write
            rights on the file.
        max_lines (int): the maximum number of lines in the file, incl. the
            lines already present. If `None`, there's no limit.
            Default to `None`.
        append (bool): if `True`, will append the data to the file.
            Otherwise, it will overwrite the file.
            Default to `True`.
        **kwargs : the keyword arguments to pass down to parent class Exporter
    .. admonition:: Example

        .. code-block:: python

            import os
            from resilient_exporters.exporters import FileExporter

            exporter = FileExporter("local_file.txt",
                                    max_lines=1000,
                                    append=False,
                                    use_memory=False, # see exporters.Exporter
                                    save_unsent_data=True)

            data = {"name": "Richard Feynman",
                    "age": 69}
            exporter.send(data)
    """
    def __init__(self,
                 target_file: Text,
                 max_lines: Optional[int] = None,
                 append: bool = True,
                 **kwargs):
        super(FileExporter, self).__init__(**kwargs)

        # Create file if it doesn't exist
        if not os.path.isfile(target_file):
            open(target_file, "x").close()
        self.__filename = target_file
        self.__max_lines = max_lines
        self.__remaining_lines = -1

        self.start(append=append)

        # Some logic in case there's a max lines
        if self.__max_lines is not None:

            # Count number of lines in file
            tmp_count = len(self.target_file.readlines())

            # Alert if the maximum is already reached
            if tmp_count >= self.__max_lines:
                logger.warning(f"""there's already {tmp_count} lines in file,
                                you asked for a maximum of {self.__max_lines}.
                                Nothing will be added to the file.""")

            # Set remaining lines
            self.__remaining_lines = self.__max_lines - tmp_count

    @property
    def remaining_lines(self) -> int:
        """It is the amount of lines the file can still contain before reaching
        the limit passed at initialisation (cf `max_lines` keyword argument at
        init). Returns 0 if there's no limit or the limit has been reached."""
        return max(self.__remaining_lines, 0)

    def write_lines(self, data: Union[Text, dict]):
        if not isinstance(data, list):
            data = [data]
        for piece in data:
            if self.__remaining_lines != 0:
                if not isinstance(piece, dict):
                    line = piece
                else:
                    line = json.dumps(piece).decode("utf-8")
                print(line, file=self.target_file)
                self.__remaining_lines -= 1
            else:
                logger.warning(f"Can't write more data in \
                                file {self.__filename}")

    """remove_lines:
       Removing by copying the file (except lines of given indices) into a
       new file, then replacing the old file with the new file. By default,
       removes the first line.
    """
    def remove_lines(self, indices: Iterable[int] = None) -> bool:
        if indices is None:
            indices = [0]
        new_filename = self.__filename + ".new"
        failed = False
        try:
            new_file = open(new_filename, "w")
            for count, line in enumerate(self.target_file):
                if count not in indices:
                    new_file.write(line)
        except Exception:
            failed = True
        finally:
            self.target_file.close()
            self.target_file = new_file

        if not failed:
            shutil.copyfile(new_filename, self.__filename)
            os.remove(new_filename)
            return not True
        return failed

    def send(self, data: Union[Text, dict]) -> ExportResult:
        """Writes the data into the file. Each call adds a new line in the
        file.

        Args:
            data (Union[Text, dict]): a string or `dict` with the data to
                write into the file. If a `dict`, it will be converted into a
                json document.

        Returns:
            ExportResult: if successful, returns (None, True),
                          otherwise (None, False)

        Raises:
            ExportError: if the IO stream is closed.
        """
        if self.target_file.closed:
            logger.error(f"IO stream closed for FileExporter {self.name}")
            raise ExportError(self, "Stream closed. \
                                     Has the FileExporter been stopped?")
        if self.__max_lines is None:
            self.write_lines(data)
        elif self.__remaining_lines > 0:
            self.write_lines(data)
        # @TODO a should new data replace old data if the file is full?
        # elif self.keep_new_data:
        #    self.remove_lines()
        #    self.write_lines(data)
        else:
            logger.warning(f"File {self.__filename} is full.")
            return ExportResult(None, False)
        return ExportResult(None, True)

    def start(self, append: bool = True):
        """Restarts the exporter by reopening an IO stream to the file. If there
        were no stream yet, it will create one.

        Args:
            append (bool): if True, opens the file in 'append' mode, else in
                "write" mode. Default is True.
        """
        try:
            if self.target_file.closed:
                logger.debug(f"Restarting the FileExporter {self.name}")
                self._create_stream_for_file(append)
        except AttributeError:
            # There's then no self.target_file and we should create it
            self._create_stream_for_file(append)

    def stop(self):
        """Stops the exporter, by closing the IO stream. The exporter must be
        stopped for another process to be able to read the file."""
        logger.debug(f"Stopping the FileExporter {self.name}")
        self.target_file.close()

    def _create_stream_for_file(self, append: bool = True):
        self.target_file = open(self.__filename, "a+" if append else "w+")

    def __del__(self):
        self.stop()
