from abc import abstractmethod
from dataclasses import dataclass
from typing import (
    AbstractSet,
    Dict,
    Generic,
    Iterator,
    Mapping,
    MutableMapping,
    Tuple,
    TypeVar,
    ValuesView,
)

from ._ipython_utils import ipython_key_completions_for_mapping

_Key = TypeVar("_Key")
_Value = TypeVar("_Value")

# For some reason pyright cannot create a consistent of the extended classes.
@dataclass(frozen=True)
class ImmutableMapping(Generic[_Key, _Value], Mapping[_Key, _Value]):
    """Immutable mapping."""

    _data: Dict[_Key, _Value]

    def __getitem__(self, key: _Key):
        """Get the value with the given key."""
        return self._data[key]

    def __iter__(self):
        """Return the iterator on elements."""
        return iter(self._data)

    def __len__(self):
        """Return the number of elements."""
        return len(self._data)

    def _ipython_key_completions_(self):
        return ipython_key_completions_for_mapping(self)  # type: ignore


class DelegateMutableMapping(Generic[_Key, _Value], MutableMapping[_Key, _Value]):
    """Mutable mapping backed by an underlying mapping.

    Reimplement keys, items, and values methods for performance reasons.
    See https://github.com/activeviam/atoti/pull/1162#issuecomment-592551497

    """

    @abstractmethod
    def _get_underlying(self) -> Mapping[_Key, _Value]:
        """Get the underlying mapping."""

    def __getitem__(self, key: _Key) -> _Value:
        return self._get_underlying()[key]

    def __iter__(self) -> Iterator[_Key]:
        """Return the mapping's iterator."""
        return iter(self._get_underlying())

    def __len__(self) -> int:
        """Return the number of items."""
        return len(self._get_underlying())

    def keys(self) -> AbstractSet[_Key]:
        """Return a set-like object providing a view on the keys."""
        return self._get_underlying().keys()

    def items(self) -> AbstractSet[Tuple[_Key, _Value]]:
        """Return a set-like object providing a view on the items."""
        return self._get_underlying().items()

    def values(self) -> ValuesView[_Value]:
        """Return an object providing a view on the values."""
        return self._get_underlying().values()

    def _ipython_key_completions_(self):
        return ipython_key_completions_for_mapping(self)  # type: ignore
