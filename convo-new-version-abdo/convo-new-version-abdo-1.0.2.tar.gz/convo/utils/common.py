import asyncio
import logging
import os
import shutil
import warnings
from types import TracebackType
from typing import Any, Coroutine, Dict, List, Optional, Text, Type, TypeVar

import convo.core.utils
import convo.utils.io
from convo.constants import BY_DEFAULT_LOGING_LEVEL_LIBRARY, ENVIRONMENT_LOGING_LEVEL_LIBRARY
from convo.shared.constants import CONVO_DEFAULT_LOG_LEVEL, ENVIRONMENT_LOG_LEVEL 
import convo.shared.utils.io

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TempDirPath(str):
    """Represents a path to an temporary dir. When used as a context
    manager, it erases the contents of the dir on exit.

    """

    def __enter__(self) -> "TempDirPath":
        return self

    def __exit__(
        self,
        _exc: Optional[Type[BaseException]],
        _value: Optional[Exception],
        _tb: Optional[TracebackType],
    ) -> bool:
        if os.path.exists(self):
            shutil.rmtree(self)


def reading_global_configuration(path: Text) -> Dict[Text, Any]:
    """Read global Convo configuration.

    Args:
        path: Path to the configuration
    Returns:
        The global configuration
    """
    # noinspection PyBroadException
    try:
        return convo.shared.utils.io.read_configuration_file(path)
    except Exception:
        # if things go south we pretend there is no config
        return {}


def setting_logging_level(logging_level: Optional[int] = None):
    """Set log level of Convo and Tensorflow either to the provided log level or
    to the log level specified in the environment variable 'LOG_LEVEL'. If none is set
    a default log level will be used."""

    if not logging_level:
        logging_level = os.environ.get(ENVIRONMENT_LOG_LEVEL , CONVO_DEFAULT_LOG_LEVEL)
        logging_level = logging.getLevelName(logging_level)

    logging.getLogger("convo").setLevel(logging_level)

    updating_tensor_flow_log_level()
    update_asynchronous_io_log_level()
    updating_matplot_lib_log_level()
    updating_apscheduler_log_level()
    update_socket_io_log_level()

    os.environ[ENVIRONMENT_LOG_LEVEL ] = logging.getLevelName(logging_level)


def updating_apscheduler_log_level() -> None:
    logging_level = os.environ.get(ENVIRONMENT_LOGING_LEVEL_LIBRARY, BY_DEFAULT_LOGING_LEVEL_LIBRARY)

    appscheduler_loggers = [
        "apscheduler",
        "apscheduler.scheduler",
        "apscheduler.executors",
        "apscheduler.executors.default",
    ]

    for logger_name in appscheduler_loggers:
        logging.getLogger(logger_name).setLevel(logging_level)
        logging.getLogger(logger_name).propagate = False


def update_socket_io_log_level() -> None:
    logging_level = os.environ.get(ENVIRONMENT_LOGING_LEVEL_LIBRARY, BY_DEFAULT_LOGING_LEVEL_LIBRARY)

    socket_io_loggers = ["websockets.protocol", "engineio.server", "socketio.server"]

    for logger_name in socket_io_loggers:
        logging.getLogger(logger_name).setLevel(logging_level)
        logging.getLogger(logger_name).propagate = False


def updating_tensor_flow_log_level() -> None:
    """Set the log level of Tensorflow to the log level specified in the environment
    variable 'LOG_LEVEL_LIBRARIES'."""

    # Disables libvinfer, tensorRT, cuda, AVX2 and FMA warnings (CPU support). This variable needs to be set before the
    # first import since some warnings are raised on the first import.
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

    import tensorflow as tf

    logging_level = os.environ.get(ENVIRONMENT_LOGING_LEVEL_LIBRARY, BY_DEFAULT_LOGING_LEVEL_LIBRARY)

    if logging_level == "DEBUG":
        tf_log_level = tf.compat.v1.logging.DEBUG
    elif logging_level == "INFO":
        tf_log_level = tf.compat.v1.logging.INFO
    elif logging_level == "WARNING":
        tf_log_level = tf.compat.v1.logging.WARN
    else:
        tf_log_level = tf.compat.v1.logging.ERROR

    tf.compat.v1.logging.set_verbosity(tf_log_level)
    logging.getLogger("tensorflow").propagate = False


def updating_sanic_log_level(log_file: Optional[Text] = None):
    """Set the log level of sanic loggers to the log level specified in the environment
    variable 'LOG_LEVEL_LIBRARIES'."""
    from sanic.log import logger, error_logger, access_logger

    logging_level = os.environ.get(ENVIRONMENT_LOGING_LEVEL_LIBRARY, BY_DEFAULT_LOGING_LEVEL_LIBRARY)

    logger.setLevel(logging_level)
    error_logger.setLevel(logging_level)
    access_logger.setLevel(logging_level)

    logger.propagate = False
    error_logger.propagate = False
    access_logger.propagate = False

    if log_file is not None:
        formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        error_logger.addHandler(file_handler)
        access_logger.addHandler(file_handler)


def update_asynchronous_io_log_level() -> None:
    """Set the log level of asyncio to the log level specified in the environment
    variable 'LOG_LEVEL_LIBRARIES'."""
    logging_level = os.environ.get(ENVIRONMENT_LOGING_LEVEL_LIBRARY, BY_DEFAULT_LOGING_LEVEL_LIBRARY)
    logging.getLogger("asyncio").setLevel(logging_level)


def updating_matplot_lib_log_level() -> None:
    """Set the log level of matplotlib to the log level specified in the environment
    variable 'LOG_LEVEL_LIBRARIES'."""
    logging_level = os.environ.get(ENVIRONMENT_LOGING_LEVEL_LIBRARY, BY_DEFAULT_LOGING_LEVEL_LIBRARY)
    logging.getLogger("matplotlib.backends.backend_pdf").setLevel(logging_level)
    logging.getLogger("matplotlib.colorbar").setLevel(logging_level)
    logging.getLogger("matplotlib.font_manager").setLevel(logging_level)
    logging.getLogger("matplotlib.ticker").setLevel(logging_level)


def setting_logs_and_warnings_filter() -> None:
    """
    Set log filters on the root logger, and duplicate filters for warnings.

    Filters only propagate on handlers, not loggers.
    """
    for handler in logging.getLogger().handlers:
        handler.addFilter(RedoLogFilter())

    warnings.filterwarnings("once", category=UserWarning)


def obtain_verbose() -> int:
    """Returns a verbosity level according to the set log level."""
    logging_level = os.environ.get(ENVIRONMENT_LOG_LEVEL , CONVO_DEFAULT_LOG_LEVEL)

    verbosity = 0
    if logging_level == "DEBUG":
        verbosity = 2
    if logging_level == "INFO":
        verbosity = 1

    return verbosity


def sort_list_of_dictionaries_by_first_key(dicts: List[Dict]) -> List[Dict]:
    """Sorts a list of dictionaries by their first key."""
    return sorted(dicts, key=lambda d: list(d.keys())[0])


def write_global_configuration_val(name: Text, value: Any) -> bool:
    """Read global Convo configuration.

    Args:
        name: Name of the configuration key
        value: Value the configuration key should be set to

    Returns:
        `True` if the operation was successful.
    """
    # need to use `convo.constants.SUPER_USER_CONFIGURATION_PATH` to allow patching
    # in tests
    configuration_path = convo.constants.SUPER_USER_CONFIGURATION_PATH
    try:
        os.makedirs(os.path.dirname(configuration_path), exist_ok=True)

        d = reading_global_configuration(configuration_path)
        d[name] = value
        convo.shared.utils.io.writing_yaml(d, convo.constants.SUPER_USER_CONFIGURATION_PATH)
        return True
    except Exception as e:
        logger.warning(f"Failed to write global config. Error: {e}. Skipping.")
        return False


def read_global_configuration_val(name: Text, unavailable_ok: bool = True) -> Any:
    """Read a value from the global Convo configuration."""

    def not_found_check():
        if unavailable_ok:
            return None
        else:
            raise ValueError(f"Configuration '{name}' key not found.")

    # need to use `convo.constants.SUPER_USER_CONFIGURATION_PATH` to allow patching
    # in tests
    configuration_path = convo.constants.SUPER_USER_CONFIGURATION_PATH

    if not os.path.exists(configuration_path):
        return not_found_check()

    d = reading_global_configuration(configuration_path)

    if name in d:
        return d[name]
    else:
        return not_found_check()


def updating_existing_keys(
    original: Dict[Any, Any], updates: Dict[Any, Any]
) -> Dict[Any, Any]:
    """Iterate through all the updates and update a value in the original dictionary.

    If the updates contain a key that is not present in the original dict, it will
    be ignored."""

    upgrade = original.copy()
    for k, v in updates.items():
        if k in upgrade:
            upgrade[k] = v
    return upgrade


class RedoLogFilter(logging.Filter):
    """Filter repeated log records."""

    end_log = None

    def filter(self, record):
        current_active_log = (
            record.levelno,
            record.pathname,
            record.lineno,
            record.msg,
            record.args,
        )
        if current_active_log != self.end_log:
            self.end_log = current_active_log
            return True
        return False


def running_in_loop(
    f: Coroutine[Any, Any, T], loop: Optional[asyncio.AbstractEventLoop] = None
) -> T:
    """Execute the awaitable in the passed loop.

    If no loop is passed, the currently existing one is used or a new one is created
    if no loop has been started in the current context.

    After the awaitable is finished, all remaining tasks on the loop will be
    awaited as well (background tasks).

    WARNING: don't use this if there are never ending background tasks scheduled.
        in this case, this function will never return.

    Args:
       f: function to execute
       loop: loop to use for the execution

    Returns:
        return value from the function
    """

    if loop is None:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    res = loop.run_until_complete(f)

    # Let's also finish all running tasks:
    awaiting = asyncio.Task.all_tasks()
    loop.run_until_complete(asyncio.gather(*awaiting))

    return res
