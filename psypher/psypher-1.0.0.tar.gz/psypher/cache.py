'''
psypher.cache - Utilities for result caching in order to improve performance.
'''

from typing import Any, Callable, TypeVar, Generic

enabled = True
instances = set()

def isenabled() -> bool:
    'Gets whether result caching is globally enabled.'
    return enabled

def setenabled(value: bool) -> None:
    'Sets whether to enable result caching.'
    global enabled
    enabled = value
    if not value:
        for instance in instances: instance.clearCache()

TResult = TypeVar('TResult')

class Cached(Generic[TResult]):
    'Represents a callable whose result is cached.'
    def __init__(self, method: Callable[..., TResult]) -> None:
        'Initializes with method to be cached.'
        self._original = method
        self._enabled = True
        self._storage = {}
        instances.add(self)
    @property
    def enabled(self) -> bool:
        'Whether caching is enabled on this instance.'
        return self._enabled and enabled
    @enabled.setter
    def enabled(self, value: bool) -> None:
        'Whether caching is enabled on this instance.'
        self._enabled = value
    def clearCache(self) -> None:
        'Clears the cache of this instance.'
        self._storage.clear()
    def __call__(self, this: Any, *args: Any, **kwargs: Any) -> TResult:
        'Returns the cached value, or compute one during initial invocation.'
        if not enabled or not self._enabled:
            return self._original(this, *args, **kwargs)
        if this not in self._storage:
            self._storage[this] = self._original(this, *args, **kwargs)
        return self._storage[this]
    def __getattr__(self, name: str) -> Any:
        'Gets the original attribute from the method.'
        return getattr(self._original, name)