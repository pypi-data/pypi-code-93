import argparse
import logging
import typing
from typing import List, Text, Optional

from convo import telemetry
from convo.cli import SubParsersAction
import convo.core.utils
import convo.shared.utils.cli
from convo.cli.arguments import export as arguments
from convo.shared.constants import EVENT_BROKERS_DOCUMENTS_URL, TRACKER_STORES_DOCUMENTS_URL
from convo.exceptions import PublishingErr
from convo.shared.exceptions import ConvoExceptions 

if typing.TYPE_CHECKING:
    from convo.core.brokers.broker import CoreEventBroker
    from convo.core.brokers.pika import PikaEventBroker
    from convo.core.tracker_store import TrackerStorage
    from convo.core.exporter import CoreExporter
    from convo.core.utils import AvailableEndpoints

logger = logging.getLogger(__name__)


def sub_parser_addition(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add subparser for `convo export`.

    Args:
        subparsers: Subparsers action object to which `argparse.ArgumentParser`
            objects can be added.
        parents: `argparse.ArgumentParser` objects whose arguments should also be
            included.
    """
    dump_parser = subparsers.add_parser(
        "export",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Export conversations using an event broker.",
    )
    dump_parser.set_defaults(func=dump_trackers)

    arguments.set_export_argument(dump_parser)


def _fetch_tracker_store(endpoints: "AvailableEndpoints") -> "TrackerStorage":
    """Get `TrackerStorage` from `endpoints`.

    Prints an error and exits if no tracker store could be loaded.

    Args:
        endpoints: `AvailableEndpoints` to initialize the tracker store from.

    Returns:
        Initialized tracker store.

    """
    if not endpoints.tracker_store:
        convo.shared.utils.cli.printing_error_exit(
            f"Could not find a `tracker_store` section in the supplied "
            f"endpoints file. Instructions on how to configure a tracker store "
            f"can be found here: {TRACKER_STORES_DOCUMENTS_URL}. "
            f"Exiting. "
        )

    from convo.core.tracker_store import TrackerStorage

    return TrackerStorage.generate(endpoints.tracker_store)


def _fetch_event_broker(endpoints: "AvailableEndpoints") -> "CoreEventBroker":
    """Get `CoreEventBroker` from `endpoints`.

    Prints an error and exits if no event broker could be loaded.

    Args:
        endpoints: `AvailableEndpoints` to initialize the event broker from.

    Returns:
        Initialized event broker.

    """
    from convo.core.brokers.broker import CoreEventBroker

    export_broker = CoreEventBroker.generate(endpoints.event_broker)

    if not export_broker:
        convo.shared.utils.cli.printing_error_exit(
            f"Could not find an `event_broker` section in the supplied "
            f"endpoints file. Instructions on how to configure an event broker "
            f"can be found here: {EVENT_BROKERS_DOCUMENTS_URL}. Exiting."
        )
    return export_broker


def _fetch_requested_conversation_ids(
    conversation_ids_arg: Optional[Text] = None,
) -> Optional[List[Text]]:
    """Get list of conversation IDs requested as a command-line argument.

    Args:
        conversation_ids_arg: Value of `--conversation-ids` command-line argument.
            If provided, this is a string of comma-separated conversation IDs.

    Return:
        List of conversation IDs requested as a command-line argument.
        `None` if that argument was left unspecified.

    """
    if not conversation_ids_arg:
        return None

    return conversation_ids_arg.split(",")


def _assert_max_timestamp_gt_min_timestamp(
    args: argparse.Namespace,
) -> None:
    """Inspect CLI timestamp parameters.

    Prints an error and exits if a maximum timestamp is provided that is smaller
    than the provided minimum timestamp.

    Args:
        args: Command-line arguments to process.

    """
    minimum_timestamp = args.minimum_timestamp
    maximum_timestamp = args.maximum_timestamp

    if (
        minimum_timestamp is not None
        and maximum_timestamp is not None
        and maximum_timestamp < minimum_timestamp
    ):
        convo.shared.utils.cli.printing_error_exit(
            f"Maximum timestamp '{maximum_timestamp}' is smaller than minimum "
            f"timestamp '{minimum_timestamp}'. Exiting."
        )


def _prepare_step_broker(event_broker: "CoreEventBroker") -> None:
    """Sets `should_keep_unpublished_messages` flag to `False` if
    `self.event_broker` is a `PikaEventBroker`.

    If publishing of events fails, the `PikaEventBroker` instance should not keep a
    list of unpublished messages, so we can retry publishing them. This is because
    the instance is launched as part of this short-lived export script, meaning the
    object is destroyed before it might be published.

    In addition, wait until the event broker reports a `ready` state.

    """
    from convo.core.brokers.pika import PikaEventBroker

    if isinstance(event_broker, PikaEventBroker):
        event_broker.should_keep_unpublished_messages = False
        event_broker.raise_on_failure = True

    if not event_broker.is_ready():
        convo.shared.utils.cli.printing_error_exit(
            f"Event broker of type '{type(event_broker)}' is not ready. Exiting."
        )


def dump_trackers(args: argparse.Namespace) -> None:
    """Export events for a connected tracker store using an event broker.

    Args:
        args: Command-line arguments to process.

    """
    _assert_max_timestamp_gt_min_timestamp(args)

    terminal = convo.core.utils.read_last_points_from_path_flow(args.endpoints)
    tracer_store = _fetch_tracker_store(terminal)
    step_broker = _fetch_event_broker(terminal)
    _prepare_step_broker(step_broker)
    request_convers_ids = _fetch_requested_conversation_ids(args.conversation_ids)

    from convo.core.exporter import CoreExporter

    exporter = CoreExporter(
        tracer_store,
        step_broker,
        args.endpoints,
        request_convers_ids,
        args.minimum_timestamp,
        args.maximum_timestamp,
    )

    try:
        published_steps = exporter.produce_events()
        telemetry.traverse_tracker_export(published_steps, tracer_store, step_broker)
        convo.shared.utils.cli.printing_success(
            f"Done! Successfully published {published_steps} events 🎉"
        )

    except PublishingErr as e:
        cmd = fetch_continuation_command(exporter, e.timestamp)
        convo.shared.utils.cli.printing_error_exit(
            f"Encountered error while publishing event with timestamp '{e}'. To "
            f"continue where I left off, run the following command:"
            f"\n\n\t{cmd}\n\nExiting."
        )

    except ConvoExceptions  as e:
        convo.shared.utils.cli.printing_error_exit(str(e))


def fetch_continuation_command(exporter: "CoreExporter", timestamp: float) -> Text:
    """Build CLI command to continue 'convo export' where it was interrupted.

    Called when event publishing stops due to an error.

    Args:
        exporter: CoreExporter object containing objects relevant for this export.
        timestamp: Timestamp of the last event attempted to be published.

    """
    # build CLI command command based on supplied timestamp and options
    command = "convo export"

    if exporter.endpoints_path is not None:
        command += f" --endpoints {exporter.endpoints_path}"

    command += f" --minimum-timestamp {timestamp}"

    if exporter.maximum_timestamp is not None:
        command += f" --maximum-timestamp {exporter.maximum_timestamp}"

    if exporter.requested_conversation_ids:
        command += (
            f" --conversation-ids {','.join(exporter.requested_conversation_ids)}"
        )

    return command
