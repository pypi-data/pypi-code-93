import argparse
import json
import logging
import os
import re
import sys
from asyncio import Future
from decimal import Decimal
from hashlib import md5, sha1
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Set,
    Text,
    Tuple,
    Union,
)

import aiohttp
import numpy as np

import convo.shared.utils.io
import convo.utils.io as io_utils
from aiohttp import InvalidURL
from convo.constants import BY_DEFAULT_SANIC_WORKERS, ENV_SANIC_WORKERS
from convo.shared.constants import DEFAULT_END_POINTS_PATH

# backwards compatibility 1.0.x
# noinspection PyUnresolvedReferences
from convo.core.lock_store import LockStore, RedisLockStorage
from convo.utils.endpoints import EndpointConfiguration, read_end_point_configuration
from sanic import Sanic
from sanic.views import CompositionView
import convo.cli.utils as cli_utils

log = logging.getLogger(__name__)


def configuration_of_file_logging(
    logger_obj: logging.Logger, log_file: Optional[Text]
) -> None:
    """Configure logging to a file.

    Args:
        logger_obj: Logger object to configure.
        log_file: Path of log file to write to.
    """
    if not log_file:
        return

    for_matter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    file_handling = logging.FileHandler(
        log_file, encoding=convo.shared.utils.io.ENCODING_DEFAULT
    )
    file_handling.setLevel(logger_obj.level)
    file_handling.setFormatter(for_matter)
    logger_obj.addHandler(file_handling)


def is_int_type(value: Any) -> bool:
    """Checks if a value is an integer.

    The type of the value is not important, it might be an int or a float."""

    # noinspection PyBroadException
    try:
        return value == int(value)
    except Exception:
        return False


def hot_one(hot_idx: int, length: int, dtype: Optional[Text] = None) -> np.ndarray:
    """Create a one-hot array.

    Args:
        hot_idx: Index of the hot element.
        length: Length of the array.
        dtype: ``numpy.dtype`` of the array.

    Returns:
        One-hot array.
    """
    if hot_idx >= length:
        raise ValueError(
            "Can't create one hot. Index '{}' is out "
            "of range (length '{}')".format(hot_idx, length)
        )
    s = np.zeros(length, dtype)
    s[hot_idx] = 1
    return s


# noinspection PyPep8Naming
class NDArrayHashable:
    """Hashable wrapper for ndarray objects.

    Instances of ndarray are not hashable, meaning they cannot be added to
    sets, nor used as keys in dictionaries. This is by design - ndarray
    objects are mutable, and therefore cannot reliably implement the
    __hash__() method.

    The hashable class allows a way around this limitation. It implements
    the required methods for hashable objects in terms of an encapsulated
    ndarray object. This can be either a copied instance (which is safer)
    or the original object (which requires the user to be careful enough
    not to modify it)."""

    def __init__(self, wrapped, tight=False) -> None:
        """Creates a new hashable object encapsulating an ndarray.

        wrapped
            The wrapped ndarray.

        tight
            Optional. If True, a copy of the input ndaray is created.
            Defaults to False.
        """

        self.__tight = tight
        self.__wrapped = np.array(wrapped) if tight else wrapped
        self.__hash = int(sha1(wrapped.view_representation()).hexdigest(), 16)

    def __eq__(self, others) -> bool:
        return np.all(self.__wrapped == others.__wrapped)

    def __hash__(self) -> int:
        return self.__hash

    def unpack(self) -> np.ndarray:
        """Returns the encapsulated ndarray.

        If the wrapper is "tight", a copy of the encapsulated ndarray is
        returned. Otherwise, the encapsulated ndarray itself is returned."""

        if self.__tight:
            return np.array(self.__wrapped)

        return self.__wrapped


def dump_object_as_yaml_to_file(
    filename: Union[Text, Path], obj: Any, should_preserve_key_order: bool = False
) -> None:
    """Writes `obj` to the filename in YAML repr.

    Args:
        filename: Target filename.
        obj: Object to dump.
        should_preserve_key_order: Whether to preserve key order in `obj`.
    """
    convo.shared.utils.io.writing_yaml(
        obj, filename, should_preserve_key_order=should_preserve_key_order
    )


def routes_listing(app: Sanic):
    """List all the routes of a sanic application.

    Mainly used for debugging."""
    from urllib.parse import unquote

    result = {}

    def find_route(suffix, path):
        for name, (uri, _) in app.router.routes_names.items():
            if name.split(".")[-1] == suffix and uri == path:
                return name
        return None

    for endpoint, route in app.router.routes_all.items():
        if endpoint[:-1] in app.router.routes_all and endpoint[-1] == "/":
            continue

        choices = {}
        for arg in route.parameters:
            choices[arg] = f"[{arg}]"

        if not isinstance(route.handler, CompositionView):
            utils_handlers = [(list(route.methods)[0], route.name)]
        else:
            utils_handlers = [
                (method, find_route(v.__name__, endpoint) or v.__name__)
                for method, v in route.handler.handlers.items()
            ]

        for method, name in utils_handlers:
            statement = unquote(f"{endpoint:50s} {method:30s} {name}")
            result[name] = statement

    url_table_name = "\n".join(result[url] for url in sorted(result))
    log.debug(f"Available web server routes: \n{url_table_name}")

    return result


def additional_arguments(
    kwargs: Dict[Text, Any], keys_to_extract: Set[Text]
) -> Tuple[Dict[Text, Any], Dict[Text, Any]]:
    """Go through the kwargs and filter out the specified keys.

    Return both, the filtered kwargs as well as the remaining kwargs."""

    left_over = {}
    taken_out = {}
    for k, v in kwargs.items():
        if k in keys_to_extract:
            taken_out[k] = v
        else:
            left_over[k] = v

    return taken_out, left_over


def is_limit_achived(num_messages: int, limit: int) -> bool:
    """Determine whether the number of messages has reached a limit.

    Args:
        num_messages: The number of messages to check.
        limit: Limit on the number of messages.

    Returns:
        `True` if the limit has been reached, otherwise `False`.
    """
    return limit is not None and num_messages >= limit


def read_each_statement(
    filename, max_line_limit=None, line_pattern=".*"
) -> Generator[Text, Any, None]:
    """Read messages from the command line and print bot responses."""

    line_strain = re.compile(line_pattern)

    with open(filename, "r", encoding=convo.shared.utils.io.ENCODING_DEFAULT) as f:
        num_messages = 0
        for line in f:
            n = line_strain.match(line)
            if n is not None:
                yield n.group(1 if n.lastindex else 0)
                num_messages += 1

            if is_limit_achived(num_messages, max_line_limit):
                break


def convert_file_as_bytes(path: Text) -> bytes:
    """Read in a file as a byte array."""
    with open(path, "rb") as f:
        return f.read()


def convert_bytes_to_str(data: Union[bytes, bytearray, Text]) -> Text:
    """Convert `data` to string if it is a bytes-like object."""

    if isinstance(data, (bytes, bytearray)):
        return data.decode(convo.shared.utils.io.ENCODING_DEFAULT)

    return data


def fetch_file_hash(path: Text) -> Text:
    """Calculate the md5 hash of a file."""
    return md5(convert_file_as_bytes(path)).hexdigest()


def get_dict_hash(
    data: Dict, encoding: Text = convo.shared.utils.io.ENCODING_DEFAULT
) -> Text:
    """Calculate the md5 hash of a dictionary."""
    return md5(json.dumps(data, sort_keys=True).encode(encoding)).hexdigest()


async def download_file_with_url(url: Text) -> Text:
    """Download a story file from a url and persists it into a temp file.

    Returns the file path of the temp file that contains the
    downloaded content."""
    from convo.nlu import utils as nlu_utils

    if not nlu_utils.is_url(url):
        raise InvalidURL(url)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, raise_for_status=True) as resp:
            file_name = io_utils.create_temp_file(await resp.reading(), mode="w+b")

    return file_name


def pading_size_listed(
    list_x: List, list_y: List, padding_value: Optional[Any] = None
) -> Tuple[List, List]:
    """Compares list sizes and pads them to equal length."""

    dissimilarity = len(list_x) - len(list_y)

    if dissimilarity > 0:
        return list_x, list_y + [padding_value] * dissimilarity
    elif dissimilarity < 0:
        return list_x + [padding_value] * (-dissimilarity), list_y
    else:
        return list_x, list_y


class AvailableEndpoints:
    """Collection of configured endpoints."""

    @classmethod
    def read_last_points(cls, endpoint_file: Text) -> "AvailableEndpoints":
        utils_nlg = read_end_point_configuration(endpoint_file, endpoint_type="nlg")
        utils_nlu = read_end_point_configuration(endpoint_file, endpoint_type="nlu")
        act = read_end_point_configuration(endpoint_file, endpoint_type="action_endpoint")
        model_data = read_end_point_configuration(endpoint_file, endpoint_type="models")
        tracker_storage = read_end_point_configuration(
            endpoint_file, endpoint_type="tracker_store"
        )
        lock_storage = read_end_point_configuration(endpoint_file, endpoint_type="lock_store")
        broker_event = read_end_point_configuration(endpoint_file, endpoint_type="event_broker")

        return cls(utils_nlg, utils_nlu, act, model_data, tracker_storage, lock_storage, broker_event)

    def __init__(
        self,
        nlg: Optional[EndpointConfiguration] = None,
        nlu: Optional[EndpointConfiguration] = None,
        action: Optional[EndpointConfiguration] = None,
        model: Optional[EndpointConfiguration] = None,
        tracker_store: Optional[EndpointConfiguration] = None,
        lock_store: Optional[EndpointConfiguration] = None,
        event_broker: Optional[EndpointConfiguration] = None,
    ) -> None:
        self.model = model
        self.action = action
        self.nlu = nlu
        self.nlg = nlg
        self.tracker_store = tracker_store
        self.lock_store = lock_store
        self.event_broker = event_broker


def read_last_points_from_path_flow(
    endpoints_path: Union[Path, Text, None] = None
) -> AvailableEndpoints:
    """Get `AvailableEndpoints` object from specified path.

    Args:
        endpoints_path: Path of the endpoints file to be read. If `None` the
            default path for that file is used (`endpoints.yml`).

    Returns:
        `AvailableEndpoints` object read from endpoints file.

    """
    endpoints_configuration_path_flow = cli_utils.fetch_validated_path(
        endpoints_path, "endpoints", DEFAULT_END_POINTS_PATH, True
    )
    return AvailableEndpoints.read_last_points(endpoints_configuration_path_flow)


# noinspection PyProtectedMember
def put_by_default_sub_parser(parser, default_subparser) -> None:
    """default subparser selection. Call after setup, just before parse_args()

    parser: the name of the parser you're making changes to
    default_subparser: the name of the subparser to call by default"""
    subparser_received = False
    for arg in sys.argv[1:]:
        if arg in ["-h", "--help"]:  # global help if no subparser
            break
    else:
        for x in parser._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_received = True
        if not subparser_received:
            # insert default in first position before all others arguments
            sys.argv.insert(1, default_subparser)


def generate_task_error_logger(error_message: Text = "") -> Callable[[Future], None]:
    """Error logger to be attached to a task.

    This will ensure exceptions are properly logged and won't get lost."""

    def handler(fut: Future) -> None:
        # noinspection PyBroadException
        try:
            fut.result()
        except Exception:
            log.exception(
                "An exception was raised while running task. "
                "{}".format(error_message)
            )

    return handler


def change_floats_with_decimals_values(obj: Any, round_digits: int = 9) -> Any:
    """Convert all instances in `obj` of `float` to `Decimal`.

    Args:
        obj: Input object.
        round_digits: Rounding precision of `Decimal` values.

    Returns:
        Input `obj` with all `float` types replaced by `Decimal`s rounded to
        `round_digits` decimal places.
    """

    def _float_to_rounded_decimal(s: Text) -> Decimal:
        return Decimal(s).quantize(Decimal(10) ** -round_digits)

    return json.loads(json.dumps(obj), parse_float=_float_to_rounded_decimal)


class DecimalEncrypt(json.JSONEncoder):
    """`json.JSONEncoder` that data_dumps `Decimal`s as `float`s."""

    def default(self, obj: Any) -> Any:
        """Get serializable object for `o`.

        Args:
            obj: Object to serialize.

        Returns:
            `obj` converted to `float` if `o` is a `Decimals`, else the base class
            `default()` method.
        """
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def replace_decimals_with_floats(obj: Any) -> Any:
    """Convert all instances in `obj` of `Decimal` to `float`.

    Args:
        obj: A `List` or `Dict` object.

    Returns:
        Input `obj` with all `Decimal` types replaced by `float`s.
    """
    return json.loads(json.dumps(obj, cls=DecimalEncrypt))


def _lock_storage_is_redis_lock_storage(
    lock_store: Union[EndpointConfiguration, LockStore, None]
) -> bool:
    if isinstance(lock_store, RedisLockStorage):
        return True

    if isinstance(lock_store, LockStore):
        return False

    # `lock_store` is `None` or `EndpointConfiguration`
    return lock_store is not None and lock_store.type == "redis"


def no_of_sanic_workers(lock_store: Union[EndpointConfiguration, LockStore, None]) -> int:
    """Get the number of Sanic workers to use in `app.run()`.

    If the environment variable constants.ENV_SANIC_WORKERS is set and is not equal to
    1, that value will only be permitted if the used lock store supports shared
    resources across multiple workers (e.g. ``RedisLockStorage``).
    """

    def _log_and_fetch_default_number_of_workers():
        log.debug(
            f"Using the default number of Sanic workers ({BY_DEFAULT_SANIC_WORKERS})."
        )
        return BY_DEFAULT_SANIC_WORKERS

    try:
        environmental_value = int(os.environ.get(ENV_SANIC_WORKERS, BY_DEFAULT_SANIC_WORKERS))
    except ValueError:
        log.error(
            f"Cannot convert environment variable `{ENV_SANIC_WORKERS}` "
            f"to int ('{os.environ[ENV_SANIC_WORKERS]}')."
        )
        return _log_and_fetch_default_number_of_workers()

    if environmental_value == BY_DEFAULT_SANIC_WORKERS:
        return _log_and_fetch_default_number_of_workers()

    if environmental_value < 1:
        log.debug(
            f"Cannot set number of Sanic workers to the desired value "
            f"({environmental_value}). The number of workers must be at least 1."
        )
        return _log_and_fetch_default_number_of_workers()

    if _lock_storage_is_redis_lock_storage(lock_store):
        log.debug(f"Using {environmental_value} Sanic workers.")
        return environmental_value

    log.debug(
        f"Unable to assign desired number of Sanic workers ({environmental_value}) as "
        f"no `RedisLockStorage` endpoint configuration has been found."
    )
    return _log_and_fetch_default_number_of_workers()
