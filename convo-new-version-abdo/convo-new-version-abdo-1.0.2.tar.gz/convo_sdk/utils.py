import asyncio
import inspect
import logging
import warnings
import os

from typing import AbstractSet, Any, List, Text, Optional, Coroutine, Union

import convo_sdk
from convo_sdk.constants import (
    SANIC_WORKERS_DEFAULT,
    SANIC_WORKERS_ENVIRONMENT,
    LOG_LEVEL_LIBS_DEFAULT,
    LOG_LEVEL_LIBS_ENVIRONMENT,
)

log = logging.getLogger(__name__)


class Element(dict):
    __acceptable_keys = ["title", "item_url", "image_url", "subtitle", "buttons"]

    def __init__(self, *args, **kwargs):
        kwargs = {
            key: value for key, value in kwargs.items() if key in self.__acceptable_keys
        }

        super().__init__(*args, **kwargs)


class Button(dict):
    pass


def all_sub_classes(cls: Any) -> List[Any]:
    """Returns all known (imported) subclasses of a class."""

    return cls.__subclasses__() + [
        g for s in cls.__subclasses__() for g in all_sub_classes(s)
    ]


def add_logging_opt_args(parser):
    """Add options to an argument parser to configure logging levels."""

    # arguments for logging configuration
    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose. Sets logging level to INFO",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
        default=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--debug",
        help="Print lots of debugging statements. Sets logging level to DEBUG",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
    )
    parser.add_argument(
        "--quiet",
        help="Be quiet! Sets logging level to WARNING",
        action="store_const",
        dest="loglevel",
        const=logging.WARNING,
    )


def color_logging_config(loglevel):
    import coloredlogs

    field_styles = coloredlogs.DEFAULT_FIELD_STYLES.copy()
    field_styles["asctime"] = {}
    level_styles = coloredlogs.DEFAULT_LEVEL_STYLES.copy()
    level_styles["debug"] = {}
    coloredlogs.install(
        level=loglevel,
        use_chroot=False,
        fmt="%(asctime)s %(levelname)-8s %(name)s  - %(message)s",
        level_styles=level_styles,
        field_styles=field_styles,
    )


def args_of(func) -> AbstractSet[Text]:
    """Return the parameters of the function `func` as a list of their names."""

    return inspect.signature(func).parameters.keys()


def no_of_sanic_workers() -> int:
    """Get the number of Sanic workers to use in `app.run()`.
    If the environment variable `constants.SANIC_WORKERS_ENVIRONMENT` is set and is not equal to 1.
    """

    def _log_and_get_default_no_of_workers():
        log.debug(
            f"Using the default number of Sanic workers ({SANIC_WORKERS_DEFAULT})."
        )
        return SANIC_WORKERS_DEFAULT

    try:
        environment_value = int(os.environ.get(SANIC_WORKERS_ENVIRONMENT, SANIC_WORKERS_DEFAULT))
    except ValueError:
        log.error(
            f"Cannot convert environment variable `{SANIC_WORKERS_ENVIRONMENT}` "
            f"to int ('{os.environ[SANIC_WORKERS_ENVIRONMENT]}')."
        )
        return _log_and_get_default_no_of_workers()

    if environment_value == SANIC_WORKERS_DEFAULT:
        return _log_and_get_default_no_of_workers()

    if environment_value < 1:
        warnings.warn(
            f"Cannot set number of Sanic workers to the desired value "
            f"({environment_value}). The number of workers must be at least 1."
        )
        return _log_and_get_default_no_of_workers()

    log.debug(f"Using {environment_value} Sanic workers.")
    return environment_value


def version_compatibility_check(convo_version: Optional[Text]) -> None:
    """Check if the version of convo and convo_sdk are compatible.

    The version check relies on the version string being formatted as
    'x.y.z' and compares whether the numbers x and y are the same for both
    convo and convo_sdk.
    Args:
        convo_version - A string containing the version of convo that
        is making the call to the action server.
    Raises:
        Warning - The version of convo version unknown or not compatible with
        this version of convo_sdk.
    """
    # Check for versions of Convo that are too old to report their version number
    if convo_version is None:
        warnings.warn(
            f"You are using an old version of convo which might "
            f"not be compatible with this version of convo_sdk "
            f"({convo_sdk.__version__}).\n"
            f"To ensure compatibility use the same version "
            f"for both, modulo the last number, i.e. using version "
            f"A.B.x the numbers A and B should be identical for "
            f"both convo and convo_sdk."
        )
        return

    convo = convo_version.split(".")[:-1]
    sdk = convo_sdk.__version__.split(".")[:-1]

    if convo != sdk:
        warnings.warn(
            f"Your versions of convo and "
            f"convo_sdk might not be compatible. You "
            f"are currently running convo version {convo_version} "
            f"and convo_sdk version {convo_sdk.__version__}.\n"
            f"To ensure compatibility use the same "
            f"version for both, modulo the last number, "
            f"i.e. using version A.B.x the numbers A and "
            f"B should be identical for "
            f"both convo and convo_sdk."
        )


def co_routine_action_check(action) -> bool:
    return inspect.iscoroutinefunction(action)


def updating_sanic_log_level() -> None:
    """Set the log level of sanic loggers.

    Use the environment variable 'LOG_LEVEL_LIBRARIES', or default to
    `LOG_LEVEL_LIBS_DEFAULT` if undefined.
    """
    from sanic.log import logger, error_logger, access_logger

    log_level = os.environ.get(LOG_LEVEL_LIBS_ENVIRONMENT, LOG_LEVEL_LIBS_DEFAULT)

    logger.setLevel(log_level)
    error_logger.setLevel(log_level)
    access_logger.setLevel(log_level)

    logger.propagate = False
    error_logger.propagate = False
    access_logger.propagate = False

async def call_potential_coroutine(
    coroutine_or_return_value: Union[Any, Coroutine]
) -> Any:
    if asyncio.iscoroutine(coroutine_or_return_value):
        return await coroutine_or_return_value

    return coroutine_or_return_value