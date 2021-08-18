import asyncio
from datetime import datetime
import functools
from functools import wraps
import hashlib
import json
import logging
import multiprocessing
import os
from pathlib import Path
import platform
import sys
import textwrap
import typing
from typing import Any, Callable, Dict, List, Optional, Text
import uuid

import async_generator
import requests
from terminaltables import SingleTable

import convo
from convo import model
from convo.constants import (
    CONFIGURATION_FILE_TELEMETRY_KEYS,
    CONFIGURATION_TELEMETRY_DATE,
    CONFIGURATION_TELEMETRY_ALLOWED,
    CONFIGURATION_TELEMETRY_ID,
)
from convo.shared.constants import TELEMETRY_DOCUMENTS_URL
from convo.shared.exceptions import ConvoExceptions
import convo.shared.utils.io
from convo.utils import common as convo_utils
import convo.utils.io

if typing.TYPE_CHECKING:
    from convo.core.brokers.broker import EventBroker
    from convo.core.tracker_store import TrackerStorage
    from convo.core.channels.channel import InputSocket
    from convo.core.agent import CoreAgent
    from convo.shared.nlu.training_data.training_data import TrainingDataSet
    from convo.shared.importers.importer import TrainingDataImporter
    from convo.core.utils import AvailableEndpoints


logging = logging.getLogger(__name__)

LAST_SEGMENT = "https://api.segment.io/v1/track"
SEGMENT_REQUEST_TIMEOUT_COMPLETED = 5  # seconds

TELEMETRY_ENABLED_ENV_VAR = "CONVO_TELEMETRY_ENABLED"
TELEMETRY_DEBUG_ENV_VAR = "CONVO_TELEMETRY_DEBUG"

# the environment variable can be used for local development to set a test key
# e.g. `CONVO_TELEMETRY_WRITE_KEY=12354 convo train`
TELEMETRY_WRITE_KEY_ENV_VAR = "CONVO_TELEMETRY_WRITE_KEY"
EXCEPTION_WRITE_KEY_ENV_VAR = "CONVO_EXCEPTION_WRITE_KEY"

TELEMETRY_IDENTITY = "metrics_id"
BY_DEFAULT_TELEMETRY_ENABLED = True

# if one of these environment variables is set, we assume to be running in CI env
CI_ENVIRONMENT_TELL = [
    "bamboo.buildKey",
    "BUILD_ID",
    "BUILD_NUMBER",
    "BUILDKITE",
    "CI",
    "CIRCLECI",
    "CONTINUOUS_INTEGRATION",
    "GITHUB_ACTIONS",
    "HUDSON_URL",
    "JENKINS_URL",
    "TEAMCITY_VERSION",
    "TRAVIS",
]

# If updating or creating a new event, recall to update
# https://convo.com/docs/convo/telemetry
TRAINING_EVENT_BEGINS = "Training Started"
TRAINING_COMPLETED_PART = "Training Completed"
TELEMETRY_DISABLED_PART = "Telemetry Disabled"
TELEMETRY_DATA_SET_SPLIT_EVENT = "Training Data Split"
TELEMETRY_DATA_SET_VALIDATED_EVENT = "Training Data Validated"
TELEMETRY_DATA_SET_CONVERTED_EVENT = "Training Data Converted"
TELEMETRY_TRACKER_EXPORTED_PART = "Tracker Exported"
TELEMETRY_INTERACTIVE_LEARNING_STARTED_PART = "Interactive Learning Started"
TELEMETRY_SERVER_STARTED_PART = "Server Started"
TELEMETRY_PROJECT_CREATED_PART = "Project Created"
TELEMETRY_SHELL_STARTED_PART = "Shell Started"
TELEMETRY_CONVO_X_LOCAL_STARTED_EVENT = "Convo X Local Started"
TELEMETRY_VISUALIZATION_STARTED_PART = "Story Visualization Started"
TELEMETRY_TEST_CORE_PART = "Model Core Tested"
TELEMETRY_TEST_NLU_PART = "Model NLU Tested"


def print_telemetry_reporting_information() -> None:
    """Print telemetry information to std out."""
    message = textwrap.dedent(
        f"""
        Convo Open Source reports anonymous usage telemetry to help improve the product
        for all its users.

        If you'd like to opt-out, you can use `convo telemetry disable`.
        To learn more, check out {TELEMETRY_DOCUMENTS_URL}."""
    ).strip()

    telemetry_table = SingleTable([[message]])
    print(telemetry_table.table)


def _by_default_telemetry_config(is_enabled: bool) -> Dict[Text, Any]:
    return {
        CONFIGURATION_TELEMETRY_ALLOWED: is_enabled,
        CONFIGURATION_TELEMETRY_ID: uuid.uuid4().hex,
        CONFIGURATION_TELEMETRY_DATE: datetime.now(),
    }


def _write_default_telemetry_configuration(
    is_enabled: bool = BY_DEFAULT_TELEMETRY_ENABLED,
) -> bool:
    new_configuration = _by_default_telemetry_config(is_enabled)

    correct_output = convo_utils.write_global_configuration_val(
        CONFIGURATION_FILE_TELEMETRY_KEYS, new_configuration
    )

    if is_enabled and correct_output:
        print_telemetry_reporting_information()
    return correct_output


def _is_telemetry_enabled_in_config() -> bool:
    """Read telemetry configuration from the user's Convo config file in $HOME.

    Creates a default configuration if no configuration exists.

    Returns:
        `True`, if telemetry is enabled, `False` otherwise.
    """
    try:
        stored_config = convo_utils.read_global_configuration_val(
            CONFIGURATION_FILE_TELEMETRY_KEYS, unavailable_ok=False
        )

        return stored_config[CONFIGURATION_TELEMETRY_ALLOWED]
    except ValueError as e:
        logging.debug(f"Could not read telemetry settings from configuration file: {e}")

        # seems like there is no config, we'll create on and enable telemetry
        success = _write_default_telemetry_configuration()
        # if writing the configuration failed, telemetry will be disabled
        return BY_DEFAULT_TELEMETRY_ENABLED and success


def is_telemetry_enable() -> bool:
    """Check if telemetry is enabled either in configuration or environment.

    Returns:
        `True`, if telemetry is enabled, `False` otherwise.
    """
    telemetry_environment = os.environ.get(TELEMETRY_ENABLED_ENV_VAR)

    if telemetry_environment is None:
        try:
            return convo_utils.read_global_configuration_val(
                CONFIGURATION_FILE_TELEMETRY_KEYS, unavailable_ok=False
            )[CONFIGURATION_TELEMETRY_ALLOWED]
        except ValueError:
            return False
    else:
        return telemetry_environment.lower() == "true"


def load_telemetry() -> bool:
    """Read telemetry configuration from the user's Convo config file in $HOME.

    Creates a default configuration if no configuration exists.

    Returns:
        `True`, if telemetry is enabled, `False` otherwise.
    """
    try:
        # calling this even if the environment variable is set makes sure the
        # configuration is created and there is a telemetry ID
        is_enabled_in_config = _is_telemetry_enabled_in_config()

        telemetry_environment = os.environ.get(TELEMETRY_ENABLED_ENV_VAR)

        if telemetry_environment is None:
            return is_enabled_in_config
        else:
            return telemetry_environment.lower() == "true"
    except Exception as e:  # skipcq:PYL-W0703
        logging.exception(
            f"Failed to initialize telemetry reporting: {e}."
            f"Telemetry reporting will be disabled."
        )
        return False


def confirm_telemetry_enabled(f: Callable[..., Any]) -> Callable[..., Any]:
    """Function decorator for telemetry functions that ensures telemetry is enabled.

    WARNING: does not work as a decorator for async generators.

    Args:
        f: function to call if telemetry is enabled
    Returns:
        Return wrapped function
    """
    # checks if telemetry is enabled and creates a default config if this is the first
    # call to it
    load_telemetry()

    # allows us to use the decorator for async and non async functions
    if asyncio.iscoroutinefunction(f):

        @wraps(f)
        async def decorated(*args, **kwargs):
            if is_telemetry_enable():
                return await f(*args, **kwargs)
            return None

        return decorated
    else:

        @wraps(f)
        def decorated(*args, **kwargs):
            if is_telemetry_enable():
                return f(*args, **kwargs)
            return None

        return decorated


def get_write_key(tool: Text, environment_variable: Text) -> Optional[Text]:
    """Read the write key from a tool from our set of keys.

    Args:
        tool: name of the tool we want to fetch a key for
        environment_variable: name of the environment variable to set the key
    Returns:
        write key, if a key was present.
    """
    import pkg_resources
    from convo import __name__ as name

    if os.environ.get(environment_variable):
        # a write key set using the environment variable will always
        # overwrite any key provided as part of the package (`keys` file)
        return os.environ.get(environment_variable)

    write_key_path = pkg_resources.resource_filename(name, "keys")

    # noinspection PyBroadException
    try:
        with open(write_key_path) as f:
            return json.load(f).get(tool)
    except Exception:  # skipcq:PYL-W0703
        return None


def telemetry_write_keys() -> Optional[Text]:
    """Read the Segment write key from the segment key text file.
    The segment key text file should by present only in wheel/sdist packaged
    versions of Convo Open Source. This avoids running telemetry locally when
    developing on Convo or when running CI builds.

    In local development, this should always return `None` to avoid logging telemetry.

    Returns:
        Segment write key, if the key file was present.
    """

    return get_write_key("segment", TELEMETRY_WRITE_KEY_ENV_VAR)


def sentry_write_keys() -> Optional[Text]:
    """Read the sentry write key from the sentry key text file.

    Returns:
        Sentry write key, if the key file was present.
    """

    return get_write_key("sentry", EXCEPTION_WRITE_KEY_ENV_VAR)


def _encode_for_base64(original: Text, encoding: Text = "utf-8") -> Text:
    """Encodes a string as a base64 string.

    Args:
        original: Text to be encoded.
        encoding: Encoding used to convert text to binary.

    Returns:
        Encoded text.
    """
    import base64

    return base64.b64encode(original.encode(encoding)).decode(encoding)


def segment_request_headers_passed(write_key: Text) -> Dict[Text, Any]:
    """Use a segment write key to create authentication headers for the segment API.

    Args:
        write_key: Authentication key for segment.

    Returns:
        Authentication headers for segment.
    """
    return {
        "Authorization": "Basic {}".format(_encode_for_base64(write_key + ":")),
        "Content-Type": "application/json",
    }


def request_payload_part(
    distinct_id: Text,
    event_name: Text,
    properties: Dict[Text, Any],
    context: Dict[Text, Any],
) -> Dict[Text, Any]:
    """Compose a valid payload for the segment API.

    Args:
        distinct_id: Unique telemetry ID.
        event_name: Name of the event.
        properties: Values to report along the event.
        context: Context information about the event.

    Returns:
        Valid segment payload.
    """
    return {
        "userId": distinct_id,
        "event": event_name,
        "properties": properties,
        "context": context,
    }


def continuous_integration() -> bool:
    """Returns `True` if currently running inside a continuous integration context."""
    return any(env in os.environ for env in CI_ENVIRONMENT_TELL)


def _is_telemetry_debug_mode_enabled() -> bool:
    """Check if telemetry debug mode is enabled."""
    return (
            os.environ.get(TELEMETRY_DEBUG_ENV_VAR, "false").lower() == "true"
    )


def print_telemetry_event_occurrence(payload: Dict[Text, Any]) -> None:
    """Print a telemetry events payload to the commandline.

    Args:
        payload: payload of the event
    """
    print("Telemetry Event:")
    print(json.dumps(payload, indent=2))


def _passing_event(
    distinct_id: Text,
    event_name: Text,
    properties: Dict[Text, Any],
    context: Dict[Text, Any],
) -> None:
    """Report the contents segmentof an event to the /track Segment endpoint.
    Documentation: https://.com/docs/sources/server/http/

    Do not call this function from outside telemetry.py! This function does not
    check if telemetry is enabled or not.

    Args:
        distinct_id: Unique telemetry ID.
        event_name: Name of the event.
        properties: Values to report along the event.
        context: Context information about the event.
    """

    payload_data = request_payload_part(distinct_id, event_name, properties, context)

    if _is_telemetry_debug_mode_enabled():
        print_telemetry_event_occurrence(payload_data)
        return

    write_key = telemetry_write_keys()
    if not write_key:
        # If TELEMETRY_WRITE_KEY is empty or `None`, telemetry has not been
        # enabled for this build (e.g. because it is running from source)
        logging.debug("Skipping request to external service: telemetry key not set.")
        return

    headers_content = segment_request_headers_passed(write_key)

    response = requests.post(
        LAST_SEGMENT, headers=headers_content, json=payload_data, timeout=SEGMENT_REQUEST_TIMEOUT_COMPLETED
    )
    # handle different failure cases
    if response.status_code != 200:
        logging.debug(
            f"Segment telemetry request returned a {response.status_code} response. "
            f"Body: {response.text}"
        )
    else:
        data = response.json()
        if not data.get("success"):
            logging.debug(
                f"Segment telemetry request returned a failure. Response: {data}"
            )


def _hash_dir_path(path: Text) -> Optional[Text]:
    """Create a hash for the directory.

    Returns:
        hash of the directories path
    """
    complete_path = Path(path).absolute()
    return hashlib.sha256(str(complete_path).encode("utf-8")).hexdigest()


# noinspection PyBroadException
def _check_docker() -> bool:
    """Guess if we are running in docker environment.

    Returns:
        `True` if we are running inside docker, `False` otherwise.
    """
    # first we try to use the env
    try:
        os.stat("/.dockerenv")
        return True
    except Exception:  # skipcq:PYL-W0703
        pass

    # if that didn't work, try to use proc information
    try:
        return "docker" in convo.shared.utils.io.read_file("/proc/self/cgroup", "utf8")
    except Exception:  # skipcq:PYL-W0703
        return False


def with_by_default_context_fields(
    matter: Optional[Dict[Text, Any]] = None,
) -> Dict[Text, Any]:
    """Return a new context dictionary that contains the default field values merged
    with the provided ones. The default fields contain only the OS information for now.

    Args:
        matter: Context information about the event.

    Return:
        A new context.
    """
    matter = matter or {}

    return {**_by_default_context_fields(), **matter}


@functools.lru_cache()
def _by_default_context_fields() -> Dict[Text, Any]:
    """Return a dictionary that contains the default context values.

    Return:
        A new context containing information about the runtime environment.
    """
    import tensorflow as tf

    return {
        "os": {"name": platform.system(), "version": platform.release()},
        "ci": continuous_integration(),
        "project": model.proj_finger_print(),
        "directory": _hash_dir_path(os.getcwd()),
        "python": sys.version.split(" ")[0],
        "convo_open_source": convo.__version__,
        "gpu": len(tf.config.list_physical_devices("GPU")),
        "cpu": multiprocessing.cpu_count(),
        "docker": _check_docker(),
    }


def _track(
    event_name: Text,
    characteristics: Optional[Dict[Text, Any]] = None,
    context: Optional[Dict[Text, Any]] = None,
) -> None:
    """Tracks a telemetry event.

    It is OK to use this function from outside telemetry.py, but note that it
    is recommended to create a new track_xyz() function for complex telemetry
    events, or events that are generated from many parts of the Convo Open Source code.

    Args:
        event_name: Name of the event.
        characteristics: Dictionary containing the event's properties.
        context: Dictionary containing some context for this event.
    """

    


    try:
        telemetry_id = fetch_telemetry_id()

        if not telemetry_id:
            logging.debug("Will not report telemetry events as no ID was found.")
            return

        if not characteristics:
            characteristics = {}

        characteristics[TELEMETRY_IDENTITY] = telemetry_id

        _passing_event(
            telemetry_id, event_name, characteristics, with_by_default_context_fields(context)
        )
        

    except Exception as e:  # skipcq:PYL-W0703
        

        logging.debug(f"Skipping telemetry reporting: {e}")


def fetch_telemetry_id() -> Optional[Text]:
    """Return the unique telemetry identifier for this Convo Open Source install.
    The identifier can be any string, but it should be a UUID.

    Returns:
        The identifier, if it is configured correctly.
    """

    try:
        telemetry_config = (
            convo_utils.read_global_configuration_val(CONFIGURATION_FILE_TELEMETRY_KEYS) or {}
        )

        return telemetry_config.get(CONFIGURATION_TELEMETRY_ID)
    except Exception as e:  # skipcq:PYL-W0703
        logging.debug(f"Unable to retrieve telemetry ID: {e}")
        return None


def toggle_telemetry_report(is_enabled: bool) -> None:
    """Write to the configuration if telemetry tracking should be enabled or disabled.

    Args:
        is_enabled: `True` if the telemetry reporting should be enabled,
            `False` otherwise.
    """

    configuration = convo_utils.read_global_configuration_val(CONFIGURATION_FILE_TELEMETRY_KEYS)

    if configuration:
        configuration[CONFIGURATION_TELEMETRY_ALLOWED] = is_enabled
    else:
        configuration = _by_default_telemetry_config(is_enabled)

    convo_utils.write_global_configuration_val(CONFIGURATION_FILE_TELEMETRY_KEYS, configuration)


def pick_sensitive_data_from_sentry_event(
    event: Dict[Text, Any], _unused_hint: Optional[Dict[Text, Any]] = None
) -> Optional[Dict[Text, Any]]:
    """Remove any sensitive data from the event (e.g. path names).

    Args:
        event: event to be logged to sentry
        _unused_hint: some hinting information sent alongside of the event

    Returns:
        the event without any sensitive / PII data or `None` if the event should
        be discarded.
    """
    # removes any convo_paths from stack traces (avoids e.g. sending
    # a users home dir name if package is installed there)
    for value in event.get("exception", {}).get("values", []):
        for frame in value.get("stacktrace", {}).get("frames", []):
            frame["abs_path"] = ""

            if f"convo_sdk{os.path.sep}executor.py" in frame["filename"]:
                # this looks a lot like an exception in the SDK and hence custom code
                # no need for us to deal with that
                return None
            elif "site-packages" in frame["filename"]:
                # drop site-packages and following slash / backslash
                relative_name = frame["filename"].split("site-packages")[-1][1:]
                frame["filename"] = os.path.join("site-packages", relative_name)
            elif "dist-packages" in frame["filename"]:
                # drop dist-packages and following slash / backslash
                relative_name = frame["filename"].split("dist-packages")[-1][1:]
                frame["filename"] = os.path.join("dist-packages", relative_name)
            elif os.path.isabs(frame["filename"]):
                # if the file path is absolute, we'll drop the whole event as this is
                # very likely custom code. needs to happen after cleaning as
                # site-packages / dist-packages convo_paths are also absolute, but fine.
                return None
    return event


@confirm_telemetry_enabled
def start_error_reporting() -> None:
    """Sets up automated error reporting.

    Exceptions are reported to sentry. We avoid sending any metadata (local
    variables, convo_paths, ...) to make sure we don't compromise any data. Only the
    exception and its stacktrace is logged and only if the exception origins
    from the `convo` package."""
    import sentry_sdk
    from sentry_sdk import configure_scope
    from sentry_sdk.integrations.atexit import AtexitIntegration
    from sentry_sdk.integrations.dedupe import DedupeIntegration
    from sentry_sdk.integrations.excepthook import ExcepthookIntegration

    # key for local testing can be found at
    # https://sentry.io/settings/convohq/projects/convo-open-source/install/python/
    # for local testing, set the key using `CONVO_EXCEPTION_WRITE_KEY=key convo <command>`
    key = sentry_write_keys()

    if not key:
        return

    telemetry_id = fetch_telemetry_id()

    # this is a very defensive configuration, avoiding as many integrations as
    # possible. it also submits very little data (exception with error message
    # and line numbers).
    sentry_sdk.init(
        f"https://{key}.ingest.sentry.io/2801673",
        before_send=pick_sensitive_data_from_sentry_event,
        integrations=[
            ExcepthookIntegration(),
            DedupeIntegration(),
            AtexitIntegration(lambda _, __: None),
        ],
        send_default_pii=False,  # activate PII filter
        server_name=telemetry_id or "UNKNOWN",
        ignore_errors=[KeyboardInterrupt, ConvoExceptions ],
        in_app_include=["convo"],  # only submit errors in this package
        with_locals=False,  # don't submit local variables
        release=f"convo-{convo.__version__}",
        default_integrations=False,
        environment="development" if continuous_integration() else "production",
    )

    if telemetry_id:
        with configure_scope() as scope:
            scope.set_user({"id": telemetry_id})


@async_generator.asynccontextmanager
async def track_model_training(
    training_data: "TrainingDataImporter", model_type: Text
) -> typing.AsyncGenerator[None, None]:
    """Track a model training started.

    WARNING: since this is a generator, it can't use the ensure telemetry
        decorator. We need to manually add these checks here. This can be
        fixed as soon as we drop python 3.6 support.

    Args:
        training_data: Training data used for the training.
        model_type: Specifies the type of training, should be either "convo", "core"
            or "nlu".
    """
    if not load_telemetry():
        # telemetry reporting is disabled. we won't do any reporting
        yield  # runs the training
        return  # closes the async context

    config = await training_data.get_config()
    story = await training_data.fetch_stories()
    nlu_data_set = await training_data.fetch_nlu_data()
    domain_name = await training_data.domain()
    
    training_identity = uuid.uuid4().hex

    

    
    _track(
        TRAINING_EVENT_BEGINS,
        {
            "language": config.get("language"),
            "training_id": training_identity,
            "type": model_type,
            "pipeline": config.get("pipeline"),
            "policies": config.get("policies"),
            "num_intent_examples": len(nlu_data_set.intent_exp),
            "num_entity_examples": len(nlu_data_set.entity_exp),
            "num_actions": len(domain_name.action_names),
            # Old nomenclature from when 'responses' were still called
            # 'templates' in the domain
            "num_templates": len(domain_name.templates),
            "num_slots": len(domain_name.slots),
            "num_forms": len(domain_name.forms),
            "num_intents": len(domain_name.fetch_intents),
            "num_entities": len(domain_name.entities),
            "num_story_steps": len(story.story_steps),
            "num_lookup_tables": len(nlu_data_set.lookup_tables),
            "num_synonyms": len(nlu_data_set.entity_synonyms),
            "num_regexes": len(nlu_data_set.regex_features),
        },
    )
    begin = datetime.now()
    yield
    run_time = datetime.now() - begin
    _track(
        TRAINING_COMPLETED_PART,
        {
            "training_id": training_identity,
            "type": model_type,
            "runtime": int(run_time.total_seconds()),
        },
    )


@confirm_telemetry_enabled
def traverse_telemetry_disabled() -> None:
    """Track when a user disables telemetry."""
    _track(TELEMETRY_DISABLED_PART)


@confirm_telemetry_enabled
def track_data_split(fraction: float, data_type: Text) -> None:
    """Track when a user splits data.

    Args:
        fraction: How much data goes into train and how much goes into test
        data_type: Is this core, nlu or nlg data
    """
    _track(TELEMETRY_DATA_SET_SPLIT_EVENT, {"fraction": fraction, "type": data_type})


@confirm_telemetry_enabled
def traverse_validate_files(validation_success: bool) -> None:
    """Track when a user validates data files.

    Args:
        validation_success: Whether the validation was successful
    """
    _track(TELEMETRY_DATA_SET_VALIDATED_EVENT, {"validation_success": validation_success})


@confirm_telemetry_enabled
def traverse_data_convert(output_format: Text, data_type: Text) -> None:
    """Track when a user converts data.

    Args:
        output_format: Target format for the converter
        data_type: Is this core, nlu or nlg data
    """
    _track(
        TELEMETRY_DATA_SET_CONVERTED_EVENT,
        {"output_format": output_format, "type": data_type},
    )


@confirm_telemetry_enabled
def traverse_tracker_export(
    number_of_exported_events: int,
    tracker_store: "TrackerStorage",
    event_broker: "EventBroker",
) -> None:
    """Track when a user exports trackers.

    Args:
        number_of_exported_events: Number of events that got exported
        tracker_store: Store used to retrieve the events from
        event_broker: Broker the events are getting published towards
    """
    _track(
        TELEMETRY_TRACKER_EXPORTED_PART,
        {
            "number_of_exported_events": number_of_exported_events,
            "tracker_store": type(tracker_store).__name__,
            "event_broker": type(event_broker).__name__,
        },
    )


@confirm_telemetry_enabled
def track_interactive_learning_start(
    skip_visualization: bool, save_in_e2e: bool
) -> None:
    """Track when a user starts an interactive learning session.

    Args:
        skip_visualization: Is visualization skipped in this session
        save_in_e2e: Is e2e used in this session
    """
    _track(
        TELEMETRY_INTERACTIVE_LEARNING_STARTED_PART,
        {"skip_visualization": skip_visualization, "save_in_e2e": save_in_e2e},
    )


@confirm_telemetry_enabled
def traverse_server_start(
    input_channels: List["InputSocket"],
    endpoints: Optional["AvailableEndpoints"],
    model_directory: Optional[Text],
    number_of_workers: int,
    is_api_enabled: bool,
) -> None:
    """Track when a user starts a convo server.

    Args:
        input_channels: Used input channels
        endpoints: Endpoint configuration for the server
        model_directory: dir of the running model
        number_of_workers: number of used Sanic workers
        is_api_enabled: whether the convo API server is enabled
    """
    from convo.core.utils import AvailableEndpoints

    def project_finger_print_existing_model(
        _model_directory: Optional[Text],
    ) -> Optional[Text]:
        """Get project fingerprint from an app's loaded model."""
        if _model_directory:
            try:
                with model.fetch_model(_model_directory) as unpacked_model:
                    finger_print = model.finger_print_from_path_flow(unpacked_model)
                    return finger_print.get(model.FINGER_PRINT_PROJ)
            except Exception:
                return None
        return None

    if not endpoints:
        endpoints = AvailableEndpoints()

    _track(
        TELEMETRY_SERVER_STARTED_PART,
        {
            "input_channels": [i.name() for i in input_channels],
            "api_enabled": is_api_enabled,
            "number_of_workers": number_of_workers,
            "endpoints_nlg": endpoints.nlg.type if endpoints.nlg else None,
            "endpoints_nlu": endpoints.nlu.type if endpoints.nlu else None,
            "endpoints_action_server": endpoints.action.type
            if endpoints.action
            else None,
            "endpoints_model_server": endpoints.model.type if endpoints.model else None,
            "endpoints_tracker_store": endpoints.tracker_store.type
            if endpoints.tracker_store
            else None,
            "endpoints_lock_store": endpoints.lock_store.type
            if endpoints.lock_store
            else None,
            "endpoints_event_broker": endpoints.event_broker.type
            if endpoints.event_broker
            else None,
            "project": project_finger_print_existing_model(model_directory),
        },
    )


@confirm_telemetry_enabled
def traverse_project_init(path: Text) -> None:
    """Track when a user creates a project using convo init.

    Args:
        path: Location of the project
    """
    _track(
        TELEMETRY_PROJECT_CREATED_PART, {"init_directory": _hash_dir_path(path)},
    )


@confirm_telemetry_enabled
def traverse_shell_started(model_type: Text) -> None:
    """Track when a user starts a bot using convo shell.

    Args:
        model_type: Type of the model, core / nlu or convo."""
    _track(TELEMETRY_SHELL_STARTED_PART, {"type": model_type})


@confirm_telemetry_enabled
def track_convo_x_local() -> None:
    """Track when a user runs Convo X in local mode."""
    _track(TELEMETRY_CONVO_X_LOCAL_STARTED_EVENT)


@confirm_telemetry_enabled
def traverse_visualization() -> None:
    """Track when a user runs the visualization."""
    _track(TELEMETRY_VISUALIZATION_STARTED_PART)


@confirm_telemetry_enabled
def traverse_core_model_test(num_story_steps: int, e2e: bool, agent: "CoreAgent") -> None:
    """Track when a user tests a core model.

    Args:
        num_story_steps: Number of test stories used for the comparison
        e2e: indicator if tests running in end to end mode
        agent: CoreAgent of the model getting tested
    """
    fingerprint = model.finger_print_from_path_flow(agent.model_directory or "")
    project = fingerprint.get(model.FINGER_PRINT_PROJ)
    _track(
        TELEMETRY_TEST_CORE_PART,
        {"project": project, "end_to_end": e2e, "num_story_steps": num_story_steps},
    )


@confirm_telemetry_enabled
def traverse_nlu_model_test(test_data: "TrainingDataSet") -> None:
    """Track when a user tests an nlu model.

    Args:
        test_data: Data used for testing
    """
    _track(
        TELEMETRY_TEST_NLU_PART,
        {
            "num_intent_examples": len(test_data.intent_exp),
            "num_entity_examples": len(test_data.entity_exp),
            "num_lookup_tables": len(test_data.lookup_tables),
            "num_synonyms": len(test_data.entity_synonyms),
            "num_regexes": len(test_data.regex_features),
        },
    )
