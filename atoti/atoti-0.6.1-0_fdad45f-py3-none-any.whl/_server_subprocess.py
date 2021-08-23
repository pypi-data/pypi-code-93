from __future__ import annotations

import os
import platform
import random
import re
import string
import time
from pathlib import Path
from subprocess import STDOUT, Popen  # nosec
from typing import TYPE_CHECKING, Collection, Tuple

from ._java_utils import JAR_PATH, get_java_path
from ._path_utils import get_atoti_home, to_absolute_path
from ._plugins import get_active_plugins

if TYPE_CHECKING:
    from .config import SessionConfig

DEFAULT_HADOOP_PATH = Path(__file__).parent / "bin" / "hadoop-2.8.1-winutils"

HADOOP_HOME = (
    Path(os.environ["HADOOP_HOME"])
    if "HADOOP_HOME" in os.environ
    else (DEFAULT_HADOOP_PATH if platform.system() == "Windows" else None)
)


def _create_session_directory() -> Path:
    """Create the directory that will contain the session files."""
    # Generate the directory name using a random string for uniqueness.
    random_string = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    session_directory = get_atoti_home() / f"{str(int(time.time()))}_{random_string}"

    # Create the session directory and its known sub-folders.
    session_directory.mkdir(parents=True)
    _compute_log_directory(session_directory).mkdir()

    return session_directory


def _compute_log_directory(session_directory: Path) -> Path:
    """Return the path the the logs directory."""
    return session_directory / "logs"


def get_plugin_jar_paths() -> Collection[str]:
    """Get the JAR paths of the available plugins."""
    return [
        str(plugin.get_jar_path())
        for plugin in get_active_plugins().values()
        if plugin.get_jar_path()
    ]


class ServerSubprocess:
    """A wrapper class to start and manage an atoti server from Python."""

    def __init__(self, *, config: SessionConfig):
        """Create and start the subprocess."""
        self._config = config
        self._session_directory = _create_session_directory()
        self._subprocess_log_file = (
            _compute_log_directory(self._session_directory) / "subprocess.log"
        )
        (self._process, self.py4j_java_port) = self._start()

    def wait(self) -> None:
        """Wait for the process to terminate.

        This will prevent the Python process to exit unless the Py4J gateway is closed since, in that case, the atoti server will stop itself.
        """
        self._process.wait()

    def _start(self) -> Tuple[Popen, int]:
        """Start the atoti server.

        Returns:
            A tuple containing the server process and the Py4J port.
        """
        process = self._create_subprocess()

        # Wait for it to start
        try:
            java_port = self._await_start()
        except Exception as error:
            process.kill()
            raise error

        # We're done
        return (process, java_port)

    def _create_subprocess(self) -> Popen:
        """Create and start the actual subprocess.

        Returns:
            The created process.
        """
        program_args = [
            str(get_java_path()),
            "-jar",
        ]

        program_args.append(f"-Dserver.session_directory={self._session_directory}")
        program_args.append("-Dserver.logging.disable_console_logging=true")

        if self._config.port is not None:
            program_args.append(f"-Dserver.port={self._config.port}")

        program_args.extend(self._config.java_options or [])

        if HADOOP_HOME:
            program_args.append(f"-Dhadoop.home.dir={to_absolute_path(HADOOP_HOME)}")

        # Put JARs from user config or from plugins into loader path
        jars = [*(self._config.extra_jars or []), *get_plugin_jar_paths()]
        if len(jars) > 0:
            program_args.append(
                f"-Dloader.path={','.join([to_absolute_path(jar) for jar in jars])}"
            )

        program_args.append(to_absolute_path(JAR_PATH))

        # Create and return the subprocess.
        # We allow the user to pass any argument to Java, even dangerous ones
        try:
            process = Popen(  # pylint: disable=consider-using-with
                program_args,
                stderr=STDOUT,
                stdout=open(  # pylint: disable=consider-using-with
                    self._subprocess_log_file, "wt"
                ),
            )  # nosec
        except Exception as error:
            raise Exception(
                f"Could not start the session. You can check the logs at {self._subprocess_log_file}",
            ) from error

        return process

    def _await_start(self) -> int:
        """Wait for the server to start and return the Py4J Java port."""
        period = 0.25
        timeout = 60
        attempt_count = round(timeout / period)
        # Wait for the process to start and log the Py4J port.
        for _attempt in range(1, attempt_count):  # pylint: disable=unused-variable
            # Look for the started line.
            try:
                with open(self._subprocess_log_file) as log_file:
                    for line in log_file:
                        regex = "Py4J server started, listening for connections on port (?P<port>[0-9]+)"
                        match = re.search(regex, line.rstrip())
                        if match:
                            # Server should be ready.
                            return int(match.group("port"))
            except FileNotFoundError:
                # The logs file has not yet been created.
                pass

            # The server is not ready yet.
            # Wait for a bit.
            time.sleep(period)

        # The inner loop did not return.
        # This means that the server could not be started correctly.
        raise Exception(
            "Could not start server. " + f"Check the logs: {self._subprocess_log_file}"
        )

    @property
    def logs_path(self) -> Path:
        """Path to the server log file."""
        return (
            _compute_log_directory(self._session_directory) / "server.log"
            if self._config.logging is None
            else Path(self._config.logging.file_path)
        )
