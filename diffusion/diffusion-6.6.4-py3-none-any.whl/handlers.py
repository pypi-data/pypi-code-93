"""Base module for various event handlers."""

import asyncio
from typing import Callable, Hashable, MutableMapping

import structlog
from typing_extensions import Protocol, runtime_checkable

from diffusion.internal import exceptions
from diffusion.internal.utils import coroutine

LOG = structlog.get_logger()


@runtime_checkable
class Handler(Protocol):
    """Protocol for event handlers implementation."""

    async def handle(self, event: str, **kwargs):
        """Implements handling of the given event.

        Args:
            event: The event identifier.
            kwargs: Additional arguments.
        """
        ...  # pragma: no cover


HandlersMapping = MutableMapping[Hashable, Handler]


class UnknownHandlerError(exceptions.DiffusionError):
    """ Raised when a requested handler key has not been registered in the session. """


class SimpleHandler(Handler):
    """ Wraps a callable into a Handler protocol instance. """

    def __init__(self, callback: Callable):
        self._callback = coroutine(callback)

    async def handle(self, event: str = "", **kwargs):
        """Implements handling of the given event.

        Args:
            event: The event identifier.
            kwargs: Additional arguments.
        """
        return await self._callback(**kwargs)


class HandlerSet(set, Handler):
    """ A collection of handlers to be invoked together. """

    async def handle(self, event: str = "", **kwargs):
        """Implements handling of the given event.

        Args:
            event: The event identifier.
            kwargs: Additional arguments.

        Returns:
            Aggregated list of returned values.
        """
        return await asyncio.gather(*[handler(**kwargs) for handler in self])


class EventStreamHandler(Handler):
    """Generic handler of event streams.

    Each keyword argument is a callable which will be converted to coroutine
    and awaited to handle the event matching the argument keyword.
    """

    def __init__(self, **kwargs: Callable):
        self._handlers = {event: coroutine(callback) for event, callback in kwargs.items()}

    async def handle(self, event: str, **kwargs):
        """Implements handling of the given event.

        Args:
            event: The event identifier.
            kwargs: Additional arguments.
        """
        try:
            handler = self._handlers[event]
        except KeyError:
            LOG.debug("No handler registered for event.", stream_event=event, **kwargs)
        else:
            return await handler(**kwargs)
