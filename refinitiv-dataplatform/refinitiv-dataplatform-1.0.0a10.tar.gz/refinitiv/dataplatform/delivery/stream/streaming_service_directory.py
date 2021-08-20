# coding: utf8

__all__ = ["StreamingServiceDirectory", "StreamingServiceDirectoryData", "ServiceEvent"]

import traceback
import logging
from threading import Lock
from enum import Enum, unique

from .stream import Stream, StreamState
from .omm_stream import OMMStream


_STREAMING_DOMAIN = "Source"


class StreamingServiceDirectoryData:
    def __init__(self, service_description):
        self._key = None
        self._name = None
        self._support_qos_range = None
        self._qos = None
        self._capabilities = []
        self._dictionaries_provided = []
        self._dictionaries_used = []
        self._vendor = None
        self._accepting_consumer_status = None
        self._service_state = 0
        # self._is_source = None
        # self._item_list = None
        # self._supports_out_of_band_snapshots = None

        self.update(service_description)

    @property
    def key(self):
        return self._key

    @property
    def name(self):
        return self._name

    @property
    def support_qos_range(self):
        return self._support_qos_range

    @property
    def qos(self):
        return self._qos

    @property
    def capabilities(self):
        return self._capabilities

    @property
    def dictionaries_provided(self):
        return self._dictionaries_provided

    @property
    def dictionaries_used(self):
        return self._dictionaries_used

    @property
    def accepting_consumer_status(self):
        return self._accepting_consumer_status

    @property
    def vendor(self):
        return self._vendor

    @property
    def service_state(self):
        return self._service_state

    def update(self, service_description):
        if service_description:
            self._key = service_description.get("Key")
            entries = (
                service_description.get("FilterList").get("Entries")
                if service_description.get("FilterList")
                else None
            )
            for entry_description in entries:
                elements = entry_description.get("Elements")
                if elements:
                    self._name = elements.get("Name", self._name)
                    self._support_qos_range = elements.get(
                        "SupportsQoSRange", self._support_qos_range
                    )
                    self._qos = elements.get("QoS", self._qos)
                    self._capabilities = elements.get(
                        "Capabilities", self._capabilities
                    )
                    dictionary = elements.get("DictionariesProvided")
                    if dictionary and dictionary.get("Data"):
                        self._dictionaries_provided = dictionary.get("Data").get("Data")
                    dictionary = elements.get("DictionariesUsed")
                    if dictionary and dictionary.get("Data"):
                        self._dictionaries_used = dictionary.get("Data").get("Data")
                    self._accepting_consumer_status = elements.get(
                        "AcceptingConsumerStatus", self._accepting_consumer_status
                    )
                    self._vendor = elements.get("Vendor", self._vendor)
                    self._service_state = elements.get(
                        "ServiceState", self._service_state
                    )

    def __repr__(self):
        return f"<Service {self._name}>"

    def __str__(self):
        return f"<{self.__class__.__name__} {self._name}>"

    @property
    def name(self):
        return self._name

    @property
    def key(self):
        return self._key

    @property
    def dictionaries(self):
        return self._dictionaries_provided


@unique
class ServiceEvent(Enum):
    Add = "Add"
    Remove = "Remove"
    Update = "Update"
    Status = "Status"
    Error = "Error"


class StreamingServiceDirectory(OMMStream):
    """This class is designed to manage service directory.

    The following are the subscription message from the stream
        - status message
        - refresh message
        - update message
        - error message
        - complete message (this is a special when the update message has a complete flag)
    """

    def __init__(self, session, connection=None):
        OMMStream.__init__(self, session, connection=connection)

        ##########################
        # Stream properties
        #   domain is Source for Service stream
        self._domain = _STREAMING_DOMAIN

        ##########################
        # StreamingServiceDirectory attributes
        self._service_map = dict()
        self._name_to_id = dict()
        self.__service_map_lock = Lock()

        ##########################
        # callback function map
        self._on = dict()

        #   store the future object when call the subscribe
        self._subscribe_future = None

    ###############################################################
    #   iterator/getitem functions

    def __iter__(self):
        #   iterate over a snapshot of constituents of this chain record
        yield from self._service_map()

    def __getitem__(self, index):
        if isinstance(index, str):
            return (
                self._service_map[self._name_to_id[index]]
                if index in self._name_to_id
                else None
            )
        else:
            return self._service_map[index] if index in self._service_map else None

    def __len__(self):
        return len(self._service_map)

    ###############################################################################
    # Service directory API

    def get_service_description(self, service):
        if isinstance(service, int):
            return self._service_map.get(service)
        else:
            # search service name in service map
            service_id = self._name_to_id.get(service)
            return self._service_map.get(service_id)

    ###############################################################
    #    methods to construct a service subscription

    def _get_open_stream_message(self):
        """ Construct and return a open message for this stream """
        assert self._with_updates is not None

        #   construct a open message
        open_message = {
            "ID": self._stream_id,
            "Type": "Request",
            "Domain": self._domain,
            "Key": {"Filter": 3},
        }

        #   done
        return open_message

    def _get_close_stream_message(self):
        """
        Construct and return a close message for this stream
        """

        #   construct a close message
        close_message = {"ID": self._stream_id, "Type": "Close"}

        #   done
        return close_message

    ###########################################
    # Callback management                     #
    def on(self, event: ServiceEvent, callback):
        self._on[event] = callback

    ###########################################
    # Process messages from stream connection #
    ###########################################
    def _on_refresh(self, message):
        with self.__service_map_lock:
            self._status = message.get("State")
            stream_state = self._status.get("Stream")
            self._code = stream_state
            self._message = self._status.get("Text")

            if self.state == StreamState.Pending:
                self._on_stream_state(StreamState.Open)

            super()._on_refresh(message)

            if self.state is not StreamState.Closed:
                # Decode Entries from refresh message
                self._on_message(message)

    def _on_update(self, update):
        with self.__service_map_lock:
            super()._on_update(update)
            if self.state is not StreamState.Closed:
                self._on_stream_state(StreamState.Open)

    def _on_status(self, status):
        with self.__service_map_lock:
            state = status.get("State")
            stream_state = state.get("Stream")
            self._code = stream_state
            self._message = state.get("Text")

            if stream_state in ["Closed", "ClosedRecover", "NonStreaming", "Redirect"]:
                self._state = StreamState.Closed
                self._code = state.get("Code")
                self._session.log(
                    1, "Set stream {} as {}".format(self.stream_id, self._state)
                )
            # Notify status ?
            self._notify(ServiceEvent.Status, status)
            super()._on_status(status)

    def _on_error(self, error):
        with self.__service_map_lock:
            super()._on_error(error)
            if self.state is not StreamState.Closed:
                self._message = error
                self._notify(ServiceEvent.Error, error)

    def _on_message(self, message):
        if message.get("Map") and message.get("Map").get("Entries"):
            entries = message.get("Map").get("Entries")
            for entry in entries:
                action = entry.get("Action")
                service_key = entry.get("Key")
                if action == ServiceEvent.Add.value:
                    if service_key in self._service_map:
                        # service key is already registered
                        service = self._service_map[service_key]
                        self._session.log(
                            1,
                            f"Add twice same service {service.name}({service.key}): {entry}",
                        )
                        name = (
                            entry.get("Elements").get("Name", None)
                            if entry.get("Elements")
                            else None
                        )
                        if name != service.name:
                            self._session.log(
                                1, f"But with different service name: {name}"
                            )
                    else:
                        # New service was added
                        new_service = StreamingServiceDirectoryData(entry)
                        self._service_map[service_key] = new_service
                        self._name_to_id[new_service.name] = new_service.key
                        # Notify on new added service
                        self._notify(ServiceEvent.Add, new_service)
                elif action == ServiceEvent.Remove.value:
                    # Remove service key
                    if service_key in self._service_map:
                        service = self._service_map[service_key]
                        self._name_to_id.pop(self._name_to_id[service.name])
                        self._service_map.pop(service_key)
                        # Notify on removed service
                        self._notify(ServiceEvent.Remove, service)
                    else:
                        self._session.log(
                            1, f"Remove unknown service {service_key}: {entry}"
                        )
                elif action == ServiceEvent.Update.value:
                    # Update info on existing service
                    if service_key in self._service_map:
                        # Update info on service
                        service = self._service_map[service_key]
                        service.update(entry)
                        self._notify(ServiceEvent.Update, service)
                    else:
                        self._session.log(
                            1,
                            f"Update was received for an unknown service {service_key}: {entry}",
                        )
                elif action == ServiceEvent.Status.value:
                    if service_key in self._service_map:
                        service = self._service_map[service_key]
                        service.update(entry)
                        self._notify(ServiceEvent.Status, service)
                    else:
                        self._session.log(
                            1,
                            f"Status was received for an unknown service {service_key}: {entry}",
                        )
                elif action == ServiceEvent.Error.value:
                    if service_key in self._service_map:
                        service = self._service_map[service_key]
                        service.update(entry)
                        self._notify(ServiceEvent.Error, service)
                    else:
                        self._session.log(
                            1,
                            f"Error was received for an unknown service {service_key}: {entry}",
                        )

    def _notify(self, event_type: ServiceEvent, service: StreamingServiceDirectoryData):
        try:
            if event_type in self._on:
                self._session.log(logging.INFO, f"Call {event_type} callback")
                self._on[event_type](service)
        except Exception as e:
            self._session.log(
                logging.ERROR, f"{event_type} callback raised exception: {e!r}"
            )
            self._session.log(1, f"{traceback.format_exc()}")

    def _on_complete(self):
        with self.__service_map_lock:
            super()._on_complete()

    def _on_stream_state(self, state):
        super()._on_stream_state(state)
