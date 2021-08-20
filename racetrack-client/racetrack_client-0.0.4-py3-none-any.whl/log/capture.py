import logging
import sys
from contextlib import contextmanager
from pathlib import Path

from racetrack_client.log.debug import debug_endpoints_enabled

DEBUG_LOGS_PATH = '/tmp/ikp-rt/lifecycle.log'


@contextmanager
def save_logs():
    """Within scope of this context manager all stdout & stderr are written to a log file"""
    if not debug_endpoints_enabled():
        yield
        return

    stdout_original = sys.stdout
    stderr_original = sys.stderr
    try:
        Path(DEBUG_LOGS_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(DEBUG_LOGS_PATH, 'w') as file_stream:
            sys.stdout = ForkStreamer(stdout_original, file_stream)
            sys.stderr = ForkStreamer(stderr_original, file_stream)
            yield
    finally:
        sys.stdout = stdout_original
        sys.stderr = stderr_original


def read_logs() -> str:
    log_path = Path(DEBUG_LOGS_PATH)
    if not log_path.is_file():
        logging.warning(f"Log file doesn't exist: {log_path}")
        return ''
    return log_path.read_text()


class ForkStreamer:
    """A stream bifurcating output to two output streams."""

    def __init__(self, stream1, stream2):
        self.stream1 = stream1
        self.stream2 = stream2

    def write(self, output):
        self.stream1.write(output)
        self.stream2.write(output)

    def flush(self):
        self.stream1.flush()
        self.stream2.flush()
