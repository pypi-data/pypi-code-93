"""Custom loggers for ChillBoss."""

import logging
import sys

from colorama import Fore

# Using custom logger.
logger: logging.Logger = logging.getLogger("chillboss")

# Creating SteamHandler to log to console.
handler: logging.StreamHandler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.DEBUG)

# Custom formatter.
formatter: logging.Formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"
)


class ColorFormatter(logging.Formatter):
    """Custom Formatter for Colored logs based on the log level."""

    level_color: dict = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED,
    }

    def __init__(self):
        """Initialize the ColorFormatter object."""
        super().__init__(
            fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"
        )

    def format(self, record: logging.LogRecord) -> str:
        """Custom format the log string to have colored.

        Args:
            record (logging.LogRecord): LogRecord of the log.

        Returns:
            (str): Formatted log string.
        """
        return "".join(
            (
                self.level_color[record.levelno],
                super(ColorFormatter, self).format(record),
            )
        )


handler.setFormatter(ColorFormatter())
logger.addHandler(handler)

# Retaining the log level to Warning.
logger.setLevel(logging.WARNING)
