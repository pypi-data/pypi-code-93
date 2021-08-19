""" Messaging service module. """

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import structlog

from diffusion import datatypes
from diffusion.internal import protocol
from diffusion.internal.serialisers import get_serialiser
from .abstract import InboundService, OutboundService

if TYPE_CHECKING:  # pragma: no cover
    from diffusion.internal.session import InternalSession

LOG = structlog.get_logger()

CONTROL_GROUP_DEFAULT = "default"


class MessagingSend(OutboundService, InboundService):
    """ Request-Response service. """

    service_id = 85
    name = "MESSAGING_SEND"
    request_serialiser = get_serialiser("messaging-send-request")
    response_serialiser = get_serialiser("messaging-response")

    def _read_response(self, stream: io.BytesIO) -> None:
        datatype_name, response_value = self.response_serialiser.read(stream)
        response = datatypes.get(datatype_name).from_bytes(response_value)
        self.response.set(response)

    def _read_request(self, stream: io.BytesIO) -> None:
        path, datatype_name, response_value = self.request_serialiser.read(stream)
        message = datatypes.get(datatype_name).from_bytes(response_value)
        self.request.set(path, message)

    async def consume(self, stream: io.BytesIO, session: InternalSession) -> None:
        """ Receive a request or response from the server. """
        if self.message_type is protocol.message_types.ServiceRequestMessage:
            self._read_request(stream)
        else:
            self._read_response(stream)

    async def produce(self, stream: io.BytesIO, session: InternalSession) -> None:
        """ Send the request to the server. """
        if self.response.serialised_value is None:
            self._write_request(stream)
        else:
            self._write_response(stream)

    async def respond(self, session: InternalSession):
        """ Send a response to a received message. """
        handler_key = (type(self), self.request["message-path"])
        response = await session.handle(handler_key, request=self.request.serialised_value)
        self.response.set(response)


class MessagingReceiverServer(OutboundService):
    """ Request-Response service - for sending requests to clients by session ID. """

    service_id = 86
    name = "MESSAGING_RECEIVER_SERVER"
    request_serialiser = get_serialiser("messaging-client-send-request")
    response_serialiser = get_serialiser("messaging-response")

    def _read_response(self, stream: io.BytesIO) -> None:
        datatype_name, response_value = self.response_serialiser.read(stream)
        response = datatypes.get(datatype_name).from_bytes(response_value)
        self.response.set(response)


class MessagingReceiverClient(InboundService):
    """ Request-Response service - for receiving requests from other clients. """

    service_id = 88
    name = "MESSAGING_RECEIVER_CLIENT"
    request_serialiser = get_serialiser("messaging-client-forward-send-request")
    response_serialiser = get_serialiser("messaging-response")

    async def respond(self, session: InternalSession):
        """ Send a response to a received message. """
        context = {
            "conversation_id": self.request["conversation-id"],
            "sender_session_id": protocol.SessionId(*self.request["session-id"]),
            "path": self.request["message-path"],
        }
        request = self.request.serialised_value
        handler_key = (type(self), self.request["message-path"])
        response = await session.handle(handler_key, request=request, **context)
        self.response.set(response)


class MessagingReceiverControlRegistration(OutboundService):
    """ Request receiver control client registration. """

    service_id = 97
    name = "MESSAGING_RECEIVER_CONTROL_REGISTRATION"
    request_serialiser = get_serialiser("message-receiver-control-registration-request")
    response_serialiser = get_serialiser()


class MessagingFilterSender(OutboundService):
    """ Request-Response service - for sending requests to clients by session ID. """

    service_id = 102
    name = "MESSAGING_FILTER_SENDER"
    request_serialiser = get_serialiser("messaging-client-filter-send-request")
    response_serialiser = get_serialiser("count-or-parser-errors2")

    def _read_response(self, stream: io.BytesIO) -> None:
        response, *_ = self.response_serialiser.read(stream)
        self.response.set(response)


class FilterResponse(InboundService):
    """ Response to a session filtered request. """

    service_id = 103
    name = "FILTER_RESPONSE"
    request_serialiser = get_serialiser("filter-response")
    response_serialiser = get_serialiser()

    async def respond(self, session: InternalSession) -> None:
        """ Respond to a filter message response. """
        conversation = session.get_conversation(self.request["conversation-id"])
        conversation.data["received"] += 1
        error, *response = self.request["filter-response"]
        if error:
            code, description = response[0]
            LOG.warning("Error reason.", code=code, description=description)
            kwargs = {"code": code, "description": description}
            handler_key: tuple = (type(self), conversation.data["filter"], "error")
        else:
            datatype, value = response
            response = datatypes.get(datatype).from_bytes(value)
            LOG.debug(f"Received response: {response}")
            kwargs = {
                "response": response,
                "session_id": protocol.SessionId(*self.request["session-id"]),
            }
            kwargs.update(conversation.data)
            handler_key = (type(self), conversation.data["filter"])
        await session.handle(handler_key, event="response", **kwargs)
        LOG.debug("Received {received} of {expected} message(s).".format(**conversation.data))
