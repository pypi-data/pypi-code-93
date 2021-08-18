import itertools
import logging
import uuid
from typing import Text, Optional, List, Set, Dict, Any

from tqdm import tqdm

import convo.cli.utils as cli_utils
import convo.shared.utils.cli
from convo.core.brokers.broker import CoreEventBroker
from convo.core.brokers.pika import PikaEventBroker
from convo.core.constants import EXPORT_PROCESS_ID_HEADER_NAME
from convo.core.tracker_store import TrackerStorage
from convo.shared.core.trackers import releaseVerbosity
from convo.exceptions import (
    NoEventsToMigrateErr,
    NoConvers_InTrackerStoreError,
    NoEventsOccurInTimeRangeError,
    PublishingErr,
)

log = logging.getLogger(__name__)


class CoreExporter:
    """Manages the publishing of events in a tracker store to an event broker.

    Attributes:
        endpoints_path: Path to the endpoints file used to configure the event
            broker and tracker store. If `None`, the default path ('endpoints.yml')
            is used.
        tracker_store: `TrackerStorage` to export conversations from.
        event_broker: `CoreEventBroker` to export conversations to.
        requested_conversation_ids: List of conversation IDs requested to be
            processed.
        minimum_timestamp: Minimum timestamp of events that are published.
            If `None`, apply no such constraint.
        maximum_timestamp: Maximum timestamp of events that are published.
            If `None`, apply no such constraint.
    """

    def __init__(
        self,
        tracker_store: TrackerStorage,
        event_broker: CoreEventBroker,
        endpoints_path: Text,
        requested_conversation_ids: Optional[Text] = None,
        minimum_timestamp: Optional[float] = None,
        maximum_timestamp: Optional[float] = None,
    ) -> None:
        self.endpoints_path = endpoints_path
        self.tracker_store = tracker_store
        # The `TrackerStorage` should return all events on `retrieve` and not just the
        # ones from the last session.
        self.tracker_store.load_events_from_previous_conversation_sessions = True

        self.event_broker = event_broker
        self.requested_conversation_ids = requested_conversation_ids
        self.minimum_timestamp = minimum_timestamp
        self.maximum_timestamp = maximum_timestamp

    def produce_events(self) -> int:
        """Publish events in a tracker store using an event broker.

        Exits if the publishing of events is interrupted due to an error. In that case,
        the CLI command to continue the export where it was interrupted is printed.

        Returns:
            The number of successfully published events.

        """
        get_events = self._get_events_within_time_scope()

        convo.shared.utils.cli.printing_information(
            f"Selected {len(get_events)} events for publishing. Ready to go 🚀"
        )

        produced_events = 0
        present_timestamp = None

        headers_name = self._fetch_msg_headers()

        for event in tqdm(get_events, "events"):
            # noinspection PyBroadException
            try:
                self._produce_with_msg_headers(event, headers_name)
                produced_events += 1
                present_timestamp = event["timestamp"]
            except Exception as e:
                log.exception(e)
                raise PublishingErr(present_timestamp)

        self.event_broker.shut()

        return produced_events

    def _fetch_msg_headers(self) -> Optional[Dict[Text, Text]]:
        """Generate a message header for publishing events to a `PikaEventBroker`.

        Returns:
            Msg headers with a randomly generated uuid under the
            `EXPORT_PROCESS_ID_HEADER_NAME` key if `self.event_broker` is a
            `PikaEventBroker`, else `None`.

        """
        if isinstance(self.event_broker, PikaEventBroker):
            return {EXPORT_PROCESS_ID_HEADER_NAME: uuid.uuid4().hex}

        return None

    def _produce_with_msg_headers(
        self, event: Dict[Text, Any], headers: Optional[Dict[Text, Text]]
    ) -> None:
        """Publish `event` to a message broker with `headers`.

        Args:
            event: Serialized event to be published.
            headers: Message headers to be published if `self.event_broker` is a
                `PikaEventBroker`.

        """
        if isinstance(self.event_broker, PikaEventBroker):
            self.event_broker.announce(event=event, headers=headers)
        else:
            self.event_broker.announce(event)

    def _fetch_conversation_ids_in_tracker(self) -> Set[Text]:
        """Fetch conversation IDs in `self.tracker_store`.

        Returns:
            A set of conversation IDs in `self.tracker_store`.

        Raises:
            `NoConvers_InTrackerStoreError` if
            `conversation_ids_in_tracker_store` is empty.

        """
        discussion_ids_tracker_store = set(self.tracker_store.keys())

        if discussion_ids_tracker_store:
            return discussion_ids_tracker_store

        raise NoConvers_InTrackerStoreError(
            "Could not find any conversations in connected tracker store. "
            "Please validate your `endpoints.yml` and make sure the defined "
            "tracker store exists. Exiting."
        )

    def _verify_all_requested_ids_exist(
        self, conversation_ids_in_tracker_store: Set[Text]
    ) -> None:
        """Warn user if `self.requested_conversation_ids` contains IDs not found in
        `conversation_ids_in_tracker_store`

        Args:
            conversation_ids_in_tracker_store: Set of conversation IDs contained in
            the tracker store.

        """
        missing_ids_in_tracker_storage = (
            set(self.requested_conversation_ids) - conversation_ids_in_tracker_store
        )
        if missing_ids_in_tracker_storage:
            convo.shared.utils.cli.printing_warning(
                f"Could not find the following requested "
                f"conversation IDs in connected tracker store: "
                f"{', '.join(sorted(missing_ids_in_tracker_storage))}"
            )

    def _fetch_conversation_ids_to_process(self) -> Set[Text]:
        """Get conversation IDs that are good for processing.

        Finds the intersection of events that are contained in the tracker store with
        those events requested as a command-line argument.

        Returns:
            Conversation IDs that are both requested and contained in the tracker
            store. If no conversation IDs are requested, all conversation IDs in the
            tracker store are returned.

        """
        discussion_ids_in_tracker_store = self._fetch_conversation_ids_in_tracker()

        if not self.requested_conversation_ids:
            return discussion_ids_in_tracker_store

        self._verify_all_requested_ids_exist(discussion_ids_in_tracker_store)

        discussion_ids_to_process = discussion_ids_in_tracker_store & set(
            self.requested_conversation_ids
        )

        if not discussion_ids_to_process:
            raise NoEventsToMigrateErr(
                "Could not find an overlap between the requested "
                "conversation IDs and those found in the tracker store. Exiting."
            )

        return discussion_ids_to_process

    def _get_events_within_time_scope(self) -> List[Dict[Text, Any]]:
        """Fetch all events for `conversation_ids` within the supplied time range.

        Returns:
            Serialized events with added `sender_id` field.

        """
        conversation_ids_to_process = self._fetch_conversation_ids_to_process()

        convo.shared.utils.cli.printing_information(
            f"Fetching events for {len(conversation_ids_to_process)} "
            f"conversation IDs:"
        )

        events = []

        for conversation_id in tqdm(conversation_ids_to_process, "conversation IDs"):
            tracker = self.tracker_store.recover(conversation_id)
            if not tracker:
                log.info(
                    f"Could not retrieve tracker for conversation ID "
                    f"'{conversation_id}'. Skipping."
                )
                continue

            _get_events = tracker.current_active_state(releaseVerbosity.ALL)["events"]

            if not _get_events:
                log.info(
                    f"No events to migrate for conversation ID '{conversation_id}'."
                )
                continue

            # the conversation IDs are needed in the event publishing
            events.extend(
                self._fetch_events_for_conversation_id(_get_events, conversation_id)
            )

        return self._sort_and_pick_events_by_timestamp(events)

    @staticmethod
    def _fetch_events_for_conversation_id(
        events: List[Dict[Text, Any]], conversation_id: Text
    ) -> List[Dict[Text, Any]]:
        """Get serialised events with added `sender_id` key.

        Args:
            events: Events to modify.
            conversation_id: Conversation ID to add to events.

        Returns:
            Events with added `sender_id` key.

        """
        events_with_discussion_id = []

        for event in events:
            event["sender_id"] = conversation_id
            events_with_discussion_id.append(event)

        return events_with_discussion_id

    def _sort_and_pick_events_by_timestamp(
        self, get_events: List[Dict[Text, Any]]
    ) -> List[Dict[Text, Any]]:
        """Sort list of events by ascending timestamp, and select events within time
        range.

        Args:
            get_events: List of serialized events to be sorted and selected from.

        Returns:
            List of serialized and sorted (by timestamp) events within the requested
            time range.

        Raises:
             `NoEventsOccurInTimeRangeError` error if no events are found within the
             requested time range.

        """
        log.debug(f"Sorting and selecting from {len(get_events)} total events found.")
        # sort the events by timestamp just in case they're not sorted already
        get_events = sorted(get_events, key=lambda x: x["timestamp"])

        # drop events failing minimum timestamp requirement
        if self.minimum_timestamp is not None:
            get_events = itertools.dropwhile(
                lambda x: x["timestamp"] < self.minimum_timestamp, get_events
            )

        # select events passing maximum timestamp requirement
        if self.maximum_timestamp is not None:
            get_events = itertools.takewhile(
                lambda x: x["timestamp"] < self.maximum_timestamp, get_events
            )

        get_events = list(get_events)
        if not get_events:
            raise NoEventsOccurInTimeRangeError(
                "Could not find any events within requested time range. Exiting."
            )

        return get_events
