from dataclasses import dataclass
from pathlib import Path
from typing import Union

from ._utils import Config, convert_path_to_absolute_string


@dataclass(frozen=True)
class LoggingConfig(Config):
    """The configuration describing how the session logs will be handled.

    Note:
        The rolling policy is:

            * A maximum file size of ``10MB``.
            * A maximum history of 7 days.

        Once the maximum size is reached, logs are archived following the pattern ``f"{file_path}.{date}.{i}.gz"`` where ``date`` is the creation date of the file in the ``yyyy-MM-dd`` format and ``i`` an integer incremented during the day.

    Example:

        >>> config = {"logging": {"file_path": "./atoti/server.log"}}

        .. doctest::
            :hide:

            >>> validate_config(config)

    """

    file_path: Union[Path, str]
    """The path of the file where the session logs will be written.

    Defaults to ``logs/server.log`` in the session directory under ``$ATOTI_HOME`` (this environment variable itself defaults to ``$HOME/.atoti``).
    """

    def __post_init__(self):
        convert_path_to_absolute_string(self, "file_path")
