import asyncio
import functools
import importlib
import logging
from typing import Text, Dict, Optional, Any, List, Callable, Collection

log = logging.getLogger(__name__)


def class_name_from_module_path(
    module_path: Text, lookup_path: Optional[Text] = None
) -> Any:
    """Given the module name and path of a class, tries to retrieve the class.

    The loaded class can be used to instantiate new objects."""
    # load the module, will raise ImportError if module cannot be loaded
    if "." in module_path:
        module_name, _, class_name = module_path.rpartition(".")
        d = importlib.import_module(module_name)
        # get the class, will raise AttributeError if class cannot be found
        return getattr(d, class_name)
    else:
        module_name = globals().get(module_path, locals().get(module_path))
        if module_name is not None:
            return module_name

        if lookup_path:
            # last resort: try to import the class from the lookup path
            d = importlib.import_module(lookup_path)
            return getattr(d, module_path)
        else:
            raise ImportError(f"Cannot retrieve class from path {module_path}.")


def all_sub_classes(cls: Any) -> List[Any]:
    """Returns all known (imported) subclasses of a class."""

    return cls.__subclasses__() + [
        g for s in cls.__subclasses__() for g in all_sub_classes(s)
    ]


def from_instance_module_path_flow(inst: Any) -> Text:
    """Return the module path of an instance's class."""
    return inst.__module__ + "." + inst.__class__.__name__


def sort_list_of_dictionaries_by_first_key(dicts: List[Dict]) -> List[Dict]:
    """Sorts a list of dictionaries by their first key."""
    return sorted(dicts, key=lambda d: list(d.keys())[0])


def lazy_property(function: Callable) -> Any:
    """Allows to avoid recomputing a property over and over.

    The result gets stored in a local var. Computation of the property
    will happen once, on the first call of the property. All
    succeeding calls will use the value stored in the private property."""

    attribute_name = "_lazy_" + function.__name__

    @property
    def lazy_property(self):
        if not hasattr(self, attribute_name):
            setattr(self, attribute_name, function(self))
        return getattr(self, attribute_name)

    return lazy_property


def caching_method(f: Callable[..., Any]) -> Callable[..., Any]:
    """Caches method calls based on the call's `args` and `kwargs`.

    Works for `async` and `sync` methods. Don't apply this to functions.

    Args:
        f: The decorated method whose return value should be cached.

    Returns:
        The return value which the method gives for the first call with the given
        arguments.
    """
    assert "self" in args_of(f), "This decorator can only be used with methods."

    class CacheData:
        """Helper class to abstract the caching details."""

        def __init__(self, caching_object: object, args: Any, kwargs: Any) -> None:
            self.caching_object = caching_object
            self.cache = getattr(caching_object, self.cache_name(), {})
            # noinspection PyUnresolvedReferences
            self.cache_key = functools._make_key(  # pytype: disable=module-attr
                args, kwargs, typed=False
            )

        def cache_name(self) -> Text:
            return f"_cached_{self.caching_object.__class__.__name__}_{f.__name__}"

        def cache_check(self) -> bool:
            return self.cache_key in self.cache

        def cache_res(self, result: Any) -> None:
            self.cache[self.cache_key] = result
            setattr(self.caching_object, self.cache_name(), self.cache)

        def cached_res(self) -> Any:
            return self.cache[self.cache_key]

    if asyncio.iscoroutinefunction(f):

        @functools.wraps(f)
        async def fun_decorated(self: object, *args: Any, **kwargs: Any) -> Any:
            cache_data = CacheData(self, args, kwargs)
            if not cache_data.cache_check():
                # Store the task immediately so that others concurrent calls of the
                # method can re-use the same task and don't schedule a second execution.
                tocache = asyncio.ensure_future(f(self, *args, **kwargs))
                cache_data.cache_res(tocache)
            return await cache_data.cached_res()

        return fun_decorated
    else:

        @functools.wraps(f)
        def fun_decorated(self: object, *args: Any, **kwargs: Any) -> Any:
            cache_data = CacheData(self, args, kwargs)
            if not cache_data.cache_check():
                tocache = f(self, *args, **kwargs)
                cache_data.cache_res(tocache)
            return cache_data.cached_res()

        return fun_decorated


def transforming_collection_to_sentence(collection: Collection[Text]) -> Text:
    """Transforms e.g. a list like ['A', 'B', 'C'] into a sentence 'A, B and C'."""
    y = list(collection)
    if len(y) >= 2:
        return ", ".join(map(str, y[:-1])) + " and " + y[-1]
    return "".join(collection)


def min_kwargs(
    kwargs: Dict[Text, Any], func: Callable, keys_excluded: Optional[List] = None
) -> Dict[Text, Any]:
    """Returns only the kwargs which are required by a function. Keys, contained in
    the exception list, are not included.

    Args:
        kwargs: All available kwargs.
        func: The function which should be called.
        keys_excluded: Keys to exclude from the result.

    Returns:
        Subset of kwargs which are accepted by `func`.

    """

    keys_excluded = keys_excluded or []

    possible_args = args_of(func)

    return {
        k: v
        for k, v in kwargs.items()
        if k in possible_args and k not in keys_excluded
    }


def mark_experimental_feature(feature_name: Text) -> None:
    """Warns users that they are using an experimental feature."""

    log.warning(
        f"The {feature_name} is currently experimental and might change or be "
        "removed in the future 🔬 Please share your feedback on it in the "
        "forum (https://forum.convo.com) to help us make this feature "
        "ready for production."
    )


def args_of(func: Callable) -> List[Text]:
    """Return the parameters of the function `func` as a list of names."""
    import inspect

    return list(inspect.signature(func).parameters.keys())
