""" Topics functionality. """
from __future__ import annotations

from typing import Any, cast, TYPE_CHECKING

import structlog

from diffusion import datatypes as dt
from diffusion.handlers import HandlerSet
from diffusion.internal.components import Component
from diffusion.internal.services.topics import TopicAddResponse
from diffusion.internal.topics import get_selector, Topic, ValueStreamHandler
from diffusion.internal.topics.constraints import UpdateConstraint, UpdateConstraintType

if TYPE_CHECKING:  # pragma: no cover
    from diffusion.session import Session

LOG = structlog.get_logger()


class Topics(Component):
    """Topics component.

    It is not supposed to be instantiated independently; an instance is available
    on each `Session` instance as `session.topics`.
    """

    CREATED = TopicAddResponse.CREATED
    EXISTS = TopicAddResponse.EXISTS

    def __init__(self, session: Session):
        super().__init__(session)
        self.session.handlers[Topic] = HandlerSet()

    @property
    def topics(self) -> dict:
        """ Internal storage for registered topics. """
        return self.session.data[Topic]

    async def add_topic(
        self, topic_path: str, specification: dt.DataTypeArgument
    ) -> TopicAddResponse:
        """Create a new topic of the given type and properties.

        Args:
            topic_path: The path to create the topic on.
            specification: Data type of the topic.
        """
        # TODO: When the TopicSpecification class is implemented, refactor this so that
        #       it accepts both DataTypeArgument and an instance of TopicSpecification
        #       as the `specification` argument (if it's a DataTypeArgument a new
        #       TopicSpecification will be constructed on the fly).
        #       (FB24373)
        topic = Topic(path=topic_path, type=dt.get(specification))
        service = self.services.TOPIC_ADD
        service.request.set(topic.path, topic.type.type_code, topic.properties)
        result = await self.session.send_request(service)
        return result["add-topic-result"]

    async def add_and_set_topic(
        self, topic_path: str, specification: dt.DataTypeArgument, value: Any
    ) -> TopicAddResponse:
        """Create a new topic of the given type and properties.

        Args:
            topic_path: The path to create the topic on.
            specification: Data type of the topic.
            value: Value to set when creating the topic. The value needs to
                   be compatible with the `topic_type`. If the topic already exists,
                   this will be set as its value.
        """
        # TODO: When the TopicSpecification class is implemented, refactor this so that
        #       it accepts both DataTypeArgument and an instance of TopicSpecification
        #       as the `specification` argument (if it's a DataTypeArgument a new
        #       TopicSpecification will be constructed on the fly).
        #       (FB24373)
        topic = Topic(path=topic_path, type=dt.get(specification))
        topic.value = value
        constraint = UpdateConstraint(UpdateConstraintType.UNCONSTRAINED_CONSTRAINT)
        service = self.services.ADD_AND_SET_TOPIC
        service.request.set(
            topic.path,
            topic.type.type_code,
            topic.properties,
            topic.binary_value,
            tuple(constraint),
        )
        result = await self.session.send_request(service)
        return result["add-topic-result"]

    async def remove_topic(self, topic_selector: str) -> int:
        """Remove all the topics that match the given selector.

        Args:
            topic_selector: The topics matching this selector will be removed
                            from the server.

        Returns:
            The number of topics removed.
        """
        service = self.services.TOPIC_REMOVAL
        service.request.set(topic_selector)
        result = await self.session.send_request(service)
        return result["integer"]

    def add_value_stream(self, topic_selector: str, stream: ValueStreamHandler) -> None:
        """Registers a value stream handler for a topic selector.

        A value stream is a series of events associated with a registered topic. This
        method adds a `ValueStream` which can handle those events.

        Args:
            topic_selector: The handler will react to the updates to all topics matching
                            this selector.
            stream: A `ValueStream` instance that handles incoming events of the
                    matching data type.
        """
        self.session.handlers[get_selector(topic_selector)] = stream

    def add_fallback_stream(self, stream: ValueStreamHandler) -> None:
        """Registers a fallback stream handler for a topic type.

        A value stream is a series of events associated with a registered topic. This
        method makes it possible to register callbacks for each of those events.

        Args:
            stream: A `ValueStream` instance that handles incoming events of the
                    matching data type.
        """
        cast(HandlerSet, self.session.handlers[Topic]).add(stream)

    async def subscribe(self, topic_selector: str):
        """Register the session to receive updates for the given topic.

        Args:
            topic_selector: The selector for topics to subscribe to.
        """
        service = self.services.SUBSCRIBE
        service.request.set(topic_selector)
        response = await self.session.send_request(service)
        return response

    async def unsubscribe(self, topic_selector: str):
        """Unregister the session to stop receiving updates for the given topic.

        Args:
            topic_selector: The selector for topics to unsubscribe from.
        """
        service = self.services.UNSUBSCRIBE
        service.request.set(topic_selector)
        response = await self.session.send_request(service)
        return response
