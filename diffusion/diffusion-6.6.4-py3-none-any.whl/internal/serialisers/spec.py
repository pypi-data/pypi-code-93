""" Specifications for serialisers, based on `spec.clj`. """

from __future__ import annotations

from collections import namedtuple
from enum import auto, Enum
from typing import Iterator, Mapping, MutableMapping, Optional, Sequence, Type, Union

import structlog

from diffusion.internal.encoded_data import Byte, Bytes, EncodingProtocol, Int32, Int64, String

LOG = structlog.get_logger()

EncodingClass = Type[EncodingProtocol]
SerialiserChain = Sequence[Optional[EncodingClass]]
SerialiserMap = MutableMapping[str, Union[EncodingClass, SerialiserChain]]
SerialiserOutput = Iterator[Optional[Type[EncodingProtocol]]]

NULL_VALUE_KEY = "void"
ENCODING_TYPE_KEYS = {
    NULL_VALUE_KEY: [],
    "BYTE": Byte,
    "BYTES": Bytes,
    "FIXED_BYTES": Bytes,
    "INT32": Int32,
    "INT64": Int64,
    "STRING": String,
}


CompoundSpec = namedtuple("CompoundSpec", "type args")


class Compound(Enum):
    """ Types of compound types. """

    def _generate_next_value_(name, start, count, last_values):
        return name

    ONE_OF = auto()
    N_OF = auto()
    SET_OF = auto()
    SORTED_SET = auto()
    MAP_OF = auto()

    def __call__(self, *args):
        """ Return an instance of the corresponding spec. """
        return CompoundSpec(type=self, args=args)


SpecItem = Union[str, CompoundSpec]
SerialiserSpecItem = Optional[Union[EncodingClass, Sequence[SpecItem], SerialiserChain]]


SERIALISER_SPECS: Mapping[str, SerialiserSpecItem] = {
    NULL_VALUE_KEY: None,
    "messaging-send-request": ("message-path", "serialised-value"),
    "messaging-client-send-request": (
        "session-id",
        "message-path",
        "serialised-value",
    ),
    "message-path": String,
    "serialised-value": ("data-type-name", "bytes"),
    "data-type-name": String,
    "bytes": Bytes,
    "messaging-response": ("serialised-value",),
    "set-topic-request": (
        "topic-path",
        "protocol14-topic-type",
        "bytes",
        "update-constraint",
    ),
    "topic-path": String,
    "protocol14-topic-type": Byte,
    "message-receiver-control-registration-request": (
        "message-receiver-control-registration-parameters",
        "conversation-id",
    ),
    "message-receiver-control-registration-parameters": (
        "service-id",
        "control-group",
        "topic-path",
        "session-property-keys",
    ),
    "conversation-id": Int64,
    "service-id": Int32,
    "control-group": String,
    "session-property-keys": Compound.SET_OF(String),
    "string": String,
    "messaging-client-forward-send-request": (
        "conversation-id",
        "session-id",
        "message-path",
        "session-properties",
        "serialised-value",
    ),
    "session-id": (Int64, Int64),
    "protocol18-log-entries-fetch-response": (
        Int64,
        Int64,
        Int64,
        Int64,
        String,
        Int64,
    ),
    "session-properties": Compound.SET_OF(String),
    "ping-request": (),
    "ping-response": (),
    "messaging-client-filter-send-request": (
        "conversation-id",
        "session-filter",
        "message-path",
        "serialised-value",
    ),
    "count-or-parser-errors2": Compound.ONE_OF({0: (Int32,), 1: ("error-report",)}),
    "error-report": (String, Int32, Int32),
    "session-filter": String,
    "create-topic-view-result": Compound.ONE_OF(
        {
            0: ("topic-view",),
            1: ("error-report",),
            2: ("error-report", "error-report"),
            3: ("error-report", "error-report", "error-report"),
            4: ("error-report", "error-report", "error-report", "error-report"),
        }
    ),
    "topic-view": ("topic-view-name", "topic-view-specification", "role-set"),
    "topic-view-name": String,
    "topic-view-specification": String,
    "role-set": Compound.SET_OF(String),
    "unconstrained-constraint": (),
    "conjunction-constraint": Compound.N_OF(
        Compound.ONE_OF(
            {
                0: ("unconstrained-constraint",),
                2: ("binary-value-constraint",),
                3: ("no-value-constraint",),
                4: ("locked-constraint",),
                5: ("no-topic-constraint",),
            }
        )
    ),
    "binary-value-constraint": Bytes,
    "no-value-constraint": (),
    "locked-constraint": ("session-lock-name", "session-lock-sequence"),
    "session-lock-name": String,
    "session-lock-sequence": Int64,
    "no-topic-constraint": (),
    "json-pointer": String,
    "partial-json-constraint": (
        Compound.MAP_OF("json-pointer", Bytes),
        # Compound.SET_OF("json-pointer"),
    ),
    "update-constraint": Compound.ONE_OF(
        {
            0: ("unconstrained-constraint",),
            1: ("conjunction-constraint",),
            2: ("binary-value-constraint",),
            3: ("no-value-constraint",),
            4: ("locked-constraint",),
            5: ("no-topic-constraint",),
            6: ("partial-json-constraint",),
        }
    ),
    "change-principal-request": ("principal", "credentials"),
    "boolean": Byte,
    "principal": String,
    "credentials": (Byte, Bytes),
    "filter-response": (
        "conversation-id",
        "session-id",
        Compound.ONE_OF({0: ("messaging-response",), 1: ("error-reason",)}),
    ),
    "error-reason": (Int32, String),
    "protocol14-topic-specification-info": (
        "topic-id",
        "topic-path",
        "protocol14-topic-specification",
    ),
    "topic-id": Int32,
    "protocol14-topic-specification": ("protocol14-topic-type", "topic-properties"),
    "topic-properties": Compound.MAP_OF("topic-property-key", String),
    "topic-property-key": String,
    "protocol14-unsubscription-notification": ("topic-id", "byte"),
    "byte": Byte,
    "protocol14-topic-add-request": ("topic-path", "protocol14-topic-specification"),
    "add-topic-result": Byte,
    "remove-topics-request": "topic-selector",
    "topic-selector": String,
    "integer": Int32,
    "authenticator-registration-parameters": ("service-id", "control-group", "handler-name"),
    "add-and-set-topic-request": (
        "topic-path",
        "protocol14-topic-specification",
        "bytes",
        "update-constraint",
    ),
    "handler-name": String,
}
