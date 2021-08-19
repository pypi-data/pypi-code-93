""" Request-response messaging functionality. """
from typing import Collection, Optional

import structlog

from diffusion import datatypes as dt
from diffusion.handlers import Handler
from diffusion.internal.components import Component
from diffusion.internal.exceptions import DiffusionError
from diffusion.internal.protocol import SessionId
from .handlers import RequestHandler

LOG = structlog.get_logger()


class Messaging(Component):
    """Messaging component.

    It is not supposed to be instantiated independently; an instance is available
    on each `Session` instance as `session.messaging`.
    """

    def add_stream_handler(
        self,
        path: str,
        handler: RequestHandler,
        addressed: bool = False,
    ) -> None:
        """Registers a request stream handler.

        The handler is invoked when the session receives a request sent
        to the given path or session filter.

        Args:
            path: The handler will respond to the requests to this path.
            handler: A Handler instance to handle the request.
            addressed: `True` to handle the requests addressed to the session's ID or
                       using a session filter; `False` for unaddressed requests.
        """
        service_type_name = "MESSAGING_SEND" if addressed else "MESSAGING_RECEIVER_CLIENT"
        service_type = type(self.services[service_type_name])
        self.session.handlers[(service_type, path)] = handler

    def add_filter_response_handler(self, session_filter: str, handler: Handler) -> None:
        """Registers a session filter response handler.

        The handler is invoked when the session receives a response
        to a request sent to the session filter.

        Args:
            session_filter: A session filtering query.
            handler: A Handler instance to handle the request.
        """
        service_type = type(self.services.FILTER_RESPONSE)
        self.session.handlers[(service_type, session_filter)] = handler

    async def register_request_handler(
        self,
        path: str,
        handler: RequestHandler,
        session_properties: Collection[str] = (),
    ) -> None:
        """Register the session as the handler for requests to a given path.

        This method is used to inform the server that any unaddressed requests to the
        given path should be forwarded to the active session. The handler to
        these requests is added at the same time, using `add_stream_handler` internally.

        Args:
            path: The handler will respond to the requests to this path.
            handler: A callable to handle the request.
            session_properties: A list of keys of session properties that should be
                                supplied with each request. To request all fixed
                                properties include `ALL_FIXED_PROPERTIES` as a key; any
                                other fixed property keys will be ignored. To request
                                all user properties include `ALL_USER_PROPERTIES` as a
                                key; any other user properties will be ignored.
        """
        self.add_stream_handler(path, handler)
        registration_service = self.services.MESSAGING_RECEIVER_CONTROL_REGISTRATION
        conversation = await self.session.conversations.new_conversation(registration_service)
        registration_service.request.set(
            *(
                self.services.MESSAGING_RECEIVER_CLIENT.service_id,
                "",
                path,
                session_properties,
                conversation.cid,
            )
        )
        await self.session.send_request(registration_service, conversation)

    async def _send_request(
        self,
        path: str,
        request: dt.DataType,
        response_type: Optional[dt.DataTypeArgument] = None,
        session_id: Optional[SessionId] = None,
    ) -> Optional[dt.DataType]:
        """Common functionality to send a request to one or more sessions.

        Args:
            path: The path to send a request to.
            request: The request to be sent, wrapped into the required `DataType` class.
            response_type: The type to convert the response to. If omitted, it will be
                           the same as the `request`'s data type.
            session_id: If specified, the request will only be sent to the session with
                        that ID. If omitted, the server will forward the request to one
                        of the sessions registered as handlers for the given `path`.

        Returns:
            The response value of the provided `response_type`.
        """
        if session_id is not None:
            service = self.services.MESSAGING_RECEIVER_SERVER
            service.request.set(session_id, path, request)
        else:
            service = self.services.MESSAGING_SEND
            service.request.set(path, request)
        response = await self.session.send_request(service)
        if response is None:
            return None
        if response_type is None:
            response_type = type(request)
        response_type = dt.get(response_type)
        if response.serialised_value.type_name != response_type.type_name:
            raise dt.InvalidDataError
        return response_type.from_bytes(response.serialised_value.to_bytes())  # type: ignore

    async def send_request_to_path(
        self,
        path: str,
        request: dt.DataType,
        response_type: Optional[dt.DataTypeArgument] = None,
    ) -> Optional[dt.DataType]:
        """Send a request to sessions based on a path.

        Args:
            path: The path to send a request to.
            request: The request to be sent, wrapped into the required `DataType` class.
            response_type: The type to convert the response to. If omitted, it will be
                           the same as the `request`'s data type.

        Returns:
            The response value of the provided `response_type`.
        """
        return await self._send_request(path=path, request=request, response_type=response_type)

    async def send_request_to_session(
        self,
        path: str,
        session_id: SessionId,
        request: dt.DataType,
        response_type: Optional[dt.DataTypeArgument] = None,
    ) -> Optional[dt.DataType]:
        """Send a request to a single session.

        Args:
            path: The path to send a request to.
            session_id: The ID of the session to send the request to.
            request: The request to be sent, wrapped into the required `DataType` class.
            response_type: The type to convert the response to. If omitted, it will be
                           the same as the `request`'s data type.

        Returns:
            The response value of the provided `response_type`.
        """
        return await self._send_request(
            path=path, request=request, response_type=response_type, session_id=session_id
        )

    async def send_request_to_filter(
        self, session_filter: str, path: str, request: dt.DataType
    ) -> int:
        """Send a request to other sessions, specified by the filter.

        Args:
            session_filter: A session filtering query.
            path: The path to send a request to.
            request: The request to be sent, wrapped into the required `DataType` class.

        Returns:
            The number of sessions that correspond to the filter, which is the number of
            responses that can be expected. When each of the responses is received, the
            handler registered for the filter will be executed.
        """
        service = self.services.MESSAGING_FILTER_SENDER
        conversation = await self.session.conversations.new_conversation(service)
        conversation.data["path"] = path
        conversation.data["filter"] = session_filter
        conversation.data["received"] = 0
        service.request.set(conversation.cid, session_filter, path, request)
        response = await self.session.send_request(service, conversation)
        error, *values = response["count-or-parser-errors2"]
        if error:
            error_message, line, column = values
            LOG.debug(
                "Received error report from the server.",
                message=error_message,
                line=line,
                column=column,
            )
            conversation.discard(error_message)
            raise MessagingError(error_message)
        else:
            conversation.data["expected"] = values[0]
            LOG.debug("Expecting responses from filter.", expected_responses=values[0])
            return values[0]


class MessagingError(DiffusionError):
    """ The generic messaging error. """
