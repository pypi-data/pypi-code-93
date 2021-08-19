from __future__ import annotations

import asyncio
from typing import (
    cast,
    Iterator,
    MutableMapping,
    Optional,
    Set,
    Type,
    TYPE_CHECKING,
    Union,
)

import attr
import cbor2 as cbor
import structlog

from diffusion import datatypes as dt
from diffusion.handlers import HandlerSet
from .selectors import Selector, get_selector
from .streams import ValueStreamHandler

if TYPE_CHECKING:  # pragma: no cover
    from diffusion.internal.session import HandlersMapping

LOG = structlog.get_logger()


@attr.s(slots=True, auto_attribs=True)
class Topic:
    """A Diffusion topic.

    Args:
        path: The topic path.
        type: Type of the topic.
        properties: A mapping of topic properties.
        id: Internal ID of the topic on this session.
        binary_value: The current value of the property. `None` by default.
        streams: A mapping of streams available for various events.
    """

    CBOR_NULL_VALUE = b"\xf6"

    path: str = attr.ib(on_setattr=attr.setters.frozen)
    type: Type[dt.DataType] = attr.ib(on_setattr=attr.setters.frozen, converter=dt.get)
    properties: MutableMapping = attr.ib(
        on_setattr=attr.setters.frozen, converter=dict, default=attr.Factory(dict)
    )
    id: Optional[int] = None
    binary_value: Optional[bytes] = attr.ib(default=None)
    streams: Set[ValueStreamHandler] = attr.ib(default=attr.Factory(set))

    @property
    def value(self):
        """ Returns the current value for the topic. """
        if self.binary_value is None:
            return None
        return self.type.from_bytes(self.binary_value).value

    @value.setter
    def value(self, value):
        self.binary_value = self.type(value).to_bytes()

    def update_streams(self, handlers: HandlersMapping) -> None:
        """Updates the collection of registered stream handlers for the topic.

        First it tries to locate any registered handlers with selectors that
        match the topic's type and path. If none are available, it selects
        the fallback stream handlers which match the topic's type.

        Args:
            handlers: The `Session.handlers` mapping containing all the registered handlers.
        """
        self.streams.update(
            handler
            for key, handler in handlers.items()
            if (
                isinstance(handler, ValueStreamHandler)
                and handler.type is self.type
                and isinstance(key, Selector)
                and key.match(self.path)
            )
        )
        if not self.streams:
            # include fallback streams
            self.streams.update(
                handler
                for key, handlers in handlers.items()
                if key is type(self) and isinstance(handlers, HandlerSet)
                for handler in handlers
                if isinstance(handler, ValueStreamHandler) and handler.type is self.type
            )

    async def handle(self, event: str, **kwargs) -> None:
        """Runs registered stream handlers for the topic and event.

        Args:
            event: Textual identifier for the event: `update`, `subscribe` etc.
            kwargs: Additional parameters. The topic's path and current value are
                    injected at runtime.
        """
        kwargs.update({"topic_path": self.path, "topic_value": self.value})
        await asyncio.gather(*(handler.handle(event, **kwargs) for handler in self.streams))

    def update(self, value: bytes, is_delta=False) -> None:
        """Updates the binary value of the topic.

        Args:
            value: The new binary value to apply.
            is_delta: If `True`, the new binary value is a binary delta to be
                   applied to the current value. If `False`, the current value
                   is replaced by the new value.
        """
        LOG.debug("Applying binary value.", value=value, is_delta=is_delta)
        if is_delta:
            value = self.apply_delta(cast(bytes, self.binary_value), value)
        self.binary_value = value

    @classmethod
    def apply_delta(cls, original: bytes, delta: bytes) -> bytes:
        """Applies a binary delta value to an original binary value.

        Args:
            original: The original binary value.
            delta: The binary delta value to apply. If this value is the CBOR
                   null value, the original value is left unchanged.
        """
        if delta == cls.CBOR_NULL_VALUE:
            return original
        new_value = b"".join(
            chunk if isinstance(chunk, bytes) else original[chunk]
            for chunk in cls.parse_delta(delta)
        )
        LOG.debug("Applying binary delta.", original=original, delta=delta, new=new_value)
        return new_value

    @classmethod
    def parse_delta(cls, delta: bytes) -> Iterator[Union[bytes, slice]]:
        """Parses a binary delta value, yielding insert and match values.

        The yielded values are either bytes to apply, or slices to be
        extracted from the original value.

        Args:
            delta: The binary delta to parse.
        """
        LOG.debug("Parsing binary delta.", delta=delta)
        length = len(delta)
        offset = 0
        match = None
        while offset < length:
            chunk = cbor.loads(delta[offset:])
            if isinstance(chunk, bytes):
                yield chunk
            elif match is None:
                match = chunk
            else:
                yield slice(match, match + chunk)
                match = None
            offset += len(cbor.dumps(chunk))
