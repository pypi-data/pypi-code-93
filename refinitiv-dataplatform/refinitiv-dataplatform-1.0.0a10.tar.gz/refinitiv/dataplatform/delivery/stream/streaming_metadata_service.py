# coding: utf8

__all__ = ["StreamingMetadataService", "FieldDescription"]


import logging
import json
import traceback

import six

from threading import Lock
from enum import Enum, unique

from refinitiv.dataplatform.core.log_reporter import LogReporter
from refinitiv.dataplatform.delivery.stream.openable import Openable

from .stream import StreamState
from .omm_stream import OMMStream
from .streaming_service_directory import ServiceEvent


_SERVICE_METADATA_DOMAIN = "Dictionary"


@unique
class ServiceMetadataEvent(Enum):
    NotInitialized = 0
    Ready = 1
    Error = 2


@unique
class MetadataType(Enum):
    RWFFld = "RWFFld"
    RWFEnum = "RWFEnum"


@unique
class RWFType(Enum):
    Unknown = 0
    Int = 3
    UInt = 4
    Float = 5
    Double = 6
    Real = 8
    Date = 9
    Time = 10
    DateTime = 11
    QOS = 12
    Status = 13
    Enumeration = 14
    Array = 15
    Buffer = 16
    StringAscii = 17
    StringUTF8 = 18
    StringRMTES = 19
    Opaque = 130
    XML = 131
    FieldList = 132
    ElementList = 133
    AnsiPage = 134
    FilterList = 135
    Vector = 136
    Map = 137
    Series = 138
    Msg = 141


class FieldDescription:
    def __init__(self, field_description):
        element = field_description.get("Elements")
        if element:
            self.name = element.get("NAME")
            self.fid = element.get("FID").get("Data") if element.get("FID") else None
            self.ripple_to = (
                element.get("RIPPLETO").get("Data") if element.get("RIPPLETO") else None
            )
            self.type = element.get("TYPE").get("Data") if element.get("TYPE") else None
            self.length = element.get("LENGTH")
            self.rwtype = element.get("RWTYPE")
            self.rwlen = element.get("RWLEN")
            self.enum_len = element.get("ENUMLENGTH")
            self.long_name = element.get("LONGNAME")

        self.enum = None

    def __str__(self):
        return json.dumps(self.__dict__)


class StreamingMetadataService(Openable, LogReporter):
    """This class is designed to manage metadata service."""

    def __init__(self, session, connection=None, service=None):
        self._session = session
        super().__init__(loop=self._session._loop, logger=self._session)

        self._connection = connection
        self._service = service

        self._field_map = dict()
        self._name_to_id = dict()

        self._enum_list = []
        self._enum_field_map = dict()

        self.__service_metadata_lock = Lock()

        self._metadata_state = dict()
        self._dictionary_stream = DictionaryStream(
            self,
            session=self._session,
            connection=self._connection,
            name=MetadataType.RWFFld.value,
            service=self._service,
            on_refresh=self._on_refresh,
            on_status=self._on_status,
            on_error=self._on_error,
        )
        self._dictionary_stream._key = {"Filter": 7, "NameType": "Name"}
        self._metadata_state[MetadataType.RWFFld] = ServiceMetadataEvent.NotInitialized

        self._enumtype_state = ServiceMetadataEvent.NotInitialized
        self._enumtype_stream = DictionaryStream(
            self,
            session=self._session,
            connection=self._connection,
            name=MetadataType.RWFEnum.value,
            service=self._service,
            on_refresh=self._on_refresh,
            on_status=self._on_status,
            on_error=self._on_error,
        )
        self._enumtype_stream._key = {"Filter": 7, "NameType": "Name"}
        self._metadata_state[MetadataType.RWFEnum] = ServiceMetadataEvent.NotInitialized

        self._stream_lock = Lock()

    ###########################################
    # Abstract implementation                 #
    def _do_resume(self):
        pass

    def _do_pause(self):
        pass

    ###########################################
    # Callback management                     #
    def on(self, event: ServiceMetadataEvent, callback):
        self._on[event] = callback

    ###############################################################################
    # Field dictionary API

    def get_field_description(self, field_ref):
        if isinstance(field_ref, int):
            return self._field_map.get(field_ref)
        elif isinstance(field_ref, str):
            fid = None
            if field_ref.isdigit():
                fid = int(field_ref)
            else:
                fid = self._name_to_id.get(field_ref)
            # search field name in field map
            return self._field_map.get(fid) if fid else None

    def get_field_enumeration(self, field_ref):
        if isinstance(field_ref, int):
            return self._enum_field_map.get(field_ref)
        elif isinstance(field_ref, str):
            fid = None
            if field_ref.isdigit():
                fid = int(field_ref)
            else:
                fid = self._name_to_id.get(field_ref)
            # search field name in field map
            return self._enum_field_map.get(fid) if fid else None

    ############################################################
    #   open/close streaming functions

    async def _do_open_async(self, with_updates=False):
        """ open field dictionary and enumtype stream and decode it"""

        six.PY3 = False

        # await asyncio.gather(self._dictionary_stream.open(False), self._enumtype_stream.open(False))
        await self._dictionary_stream.open_async(False)
        await self._enumtype_stream.open_async(False)

        if self._metadata_state == ServiceMetadataEvent.Ready:
            pass

        if self._enumtype_state == ServiceMetadataEvent.Ready:
            pass

        self.info(f"Process dictionary and enumtype requests done.")

    async def _do_close_async(self):
        pass

    def _decode_field_dictionary(self, message):
        entries = (
            message.get("Series").get("Entries") if message.get("Series") else None
        )
        if entries:
            for entry in entries:
                field_description = FieldDescription(entry)
                self._field_map[field_description.fid] = field_description
                self._name_to_id[field_description.name] = field_description.fid

    def _decode_enum_type(self, message):

        six.PY3 = True

        entries = (
            message.get("Series").get("Entries") if message.get("Series") else None
        )
        if entries:
            for entry in entries:
                values = entry["Elements"]["VALUE"]["Data"]["Data"]
                display = entry["Elements"]["DISPLAY"]["Data"]["Data"]
                enum_values = dict(zip(values, display))
                enum_value_index = len(self._enum_list)
                self._enum_list.append(enum_values)

                fids = entry["Elements"]["FIDS"]["Data"]["Data"]
                for fid in fids:
                    field_description = self._field_map.get(fid)
                    if field_description:
                        field_description.enum = enum_value_index
                    self._enum_field_map[fid] = enum_values

    ###############################################################
    #   callback functions when received messages

    def _on_refresh(self, dictionary: MetadataType, message):
        with self._stream_lock:
            self._session.log(1, f"Receive dictionary {dictionary}")
            self._metadata_state[dictionary] = ServiceMetadataEvent.NotInitialized

            if dictionary == MetadataType.RWFFld.value:
                self._decode_field_dictionary(message)
            elif dictionary == MetadataType.RWFEnum.value:
                self._decode_enum_type(message)
            # #   check this refresh is a first refresh of this subscribe item or not
            # #       it's possible that it's receiving a refresh message multiple time from server
            # if self._subscribe_response_future is not None and not self._subscribe_response_future.done():
            #     #   this is a first subscribe for this stream, so set the future to be True
            #     self._subscribe_response_future.set_result(True)

    def _on_status(self, dictionary: MetadataType, status):
        with self._stream_lock:
            self._session.log(1, f"Dictionary {self._name} - Receive status {status}")

            # #   check this error of this subscribe item
            # #       it's possible that it's receiving a error instead of refresh message from server
            # if self._subscribe_response_future is not None and not self._subscribe_response_future.done():
            #     #   this is a first subscribe for this stream, so set the future to be True
            #     self._subscribe_response_future.set_result(True)
            #
            # #   get / update stream state
            # state = status.get('State', None)
            # assert state is not None
            # stream_state = state.get('Stream', None)
            #
            # #   update state
            # if stream_state == 'Open':
            #     #   received an open stream
            #     self._state = StreamState.Open
            # elif stream_state == 'Closed':
            #     #   received an closed stream
            #     self._state = StreamState.Closed

    def _on_complete(self, dictionary: MetadataType):
        with self._stream_lock:
            if self._state in [StreamState.Pending, StreamState.Open]:
                self._session.log(1, f"Dictionary {self._name} - Receive complete")

    def _on_error(self, dictionary: MetadataType, error):
        with self._stream_lock:
            self._session.log(1, f"Dictionary[{dictionary}] - Receive error {error}")
            self._metadata_state[dictionary] = ServiceMetadataEvent.Error
            # #   check this error of this subscribe item
            # #       it's possible that it's receiving a error instead of refresh message from server
            # if self._subscribe_response_future is not None and not self._subscribe_response_future.done():
            #     #   this is a first subscribe for this stream, so set the future to be True
            #     self._subscribe_response_future.set_result(True)


class DictionaryStream(OMMStream):
    def __init__(
        self,
        svc_manager: StreamingMetadataService,
        session,
        name,
        connection=None,
        service=None,
        fields=None,
        on_refresh=None,
        on_status=None,
        on_error=None,
        on_complete=None,
    ):
        OMMStream.__init__(self, session, connection=connection)
        self._svc_manager = svc_manager

        self._name = name
        self._domain = _SERVICE_METADATA_DOMAIN
        self._service = service

        self._on = []
        self.__service_metadata_lock = Lock()

    ###########################################
    # Callback management                     #
    def on(self, event: ServiceMetadataEvent, callback):
        self._on[event] = callback

    ###########################################
    # Process messages from stream connection #
    ###########################################
    def _on_refresh(self, message):
        with self.__service_metadata_lock:
            self._status = message.get("State")
            stream_state = self._status.get("Stream")
            self._code = stream_state
            self._message = self._status.get("Text")

            super()._on_refresh(message)

            if self.state is not StreamState.Closed:
                # Decode Entries from refresh message
                self._svc_manager._on_refresh(self.name, message)

    def _on_status(self, status):
        with self.__service_metadata_lock:
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
        with self.__service_metadata_lock:
            super()._on_error(error)
            if self.state is not StreamState.Closed:
                self._message = error
                self._notify(ServiceEvent.Error, error)

    def _notify(self, event_type: ServiceEvent, message):
        try:
            if event_type in self._on:
                self._session.log(logging.INFO, f"Call {event_type} callback")
                self._on[event_type](message)
        except Exception as e:
            self._session.log(
                logging.ERROR, f"{event_type} callback raised exception: {e!r}"
            )
            self._session.log(1, f"{traceback.format_exc()}")

    def _on_complete(self):
        with self.__service_metadata_lock:
            super()._on_complete()

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
            "Key": {
                "Filter": 7,
                "Name": self.name,
                "NameType": "Name",
            },
            "Streaming": False,
        }
        if self._service:
            open_message["Key"]["Service"] = self._service

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
