"""logging utilities."""
import logging

from wpdatautil.timeit import Timer


class TimerFilter(logging.Filter):
    """Timer filter for logging."""

    # Usage ref: https://stackoverflow.com/a/61830838/

    _TIMER = Timer()

    def filter(self, record: logging.LogRecord) -> bool:
        """Add contextual information about the humanized elapsed time into the `timer` attribute of the given log record."""
        record.timer = self._TIMER  # type: ignore
        return True  # True means don't discard the record.
