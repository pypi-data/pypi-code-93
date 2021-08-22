"""The combinator base."""

import typing
from typing import Any
from dataclasses import dataclass
from redex.function import FineCallable

# pylint: disable=too-few-public-methods
class Combinator(FineCallable):
    """The base class for combinators."""

    if typing.TYPE_CHECKING:

        # pylint: disable=super-init-not-called
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            # This stub informs a type checker that this functon is implemented.
            pass

    def __init_subclass__(cls) -> None:
        """Makes subclass a dataclass."""
        super().__init_subclass__()
        dataclass(cls)
