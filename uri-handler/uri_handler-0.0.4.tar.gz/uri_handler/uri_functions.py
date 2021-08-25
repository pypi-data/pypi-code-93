import decorator
import copy
try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec

import uri_handler.handle_uris
from uri_handler.utils.uri_utils import (
    uri_prefix, uri_join)


def fitargspec(f, oldargs, oldkwargs):
    """fit function argspec given input args tuple and kwargs dict
    Parameters
    ----------
    f : func
        function to inspect
    oldargs : tuple
        arguments passed to func
    oldkwards : dict
        keyword args passed to func
    Returns
    -------
    new_args
        args with values filled in according to f spec
    new_kwargs
        kwargs with values filled in according to f spec
    """
    try:
        arginfo = getfullargspec(f)
        # args, varargs, keywords, defaults = inspect.getargspec(f)
        num_expected_args = len(arginfo.args) - len(arginfo.defaults)
        new_args = tuple(oldargs[:num_expected_args])
        new_kwargs = copy.copy(oldkwargs)
        for i, arg in enumerate(oldargs[num_expected_args:]):
            new_kwargs.update({arginfo.args[i + num_expected_args]: arg})
        return new_args, new_kwargs
    except Exception as e:
        return oldargs, oldkwargs


@decorator.decorator
def uri_func_to_uh(f, *args, **kwargs):
    # TODO anything to gain from LRU here?
    args, kwargs = fitargspec(f, args, kwargs)
    uh = kwargs.pop("uh", None)
    if uh is None:
        uh = uri_handler.handle_uris.get_uri_handler(args[0])
    kwargs['uh'] = uh
    return f(*args, **kwargs)


# TODO implement uri_handler for these convenience functions
@uri_func_to_uh
def uri_writebytes(uri, b, uh=None, *args, **kwargs):
    return uh.write_bytes(uri, b)


@uri_func_to_uh
def uri_readbytes(uri, uh=None, **kwargs):
    return uh.read_bytes(uri)


@uri_func_to_uh
def uri_list_uris(uri, uh=None, **kwargs):
    return uh.list_uris_prefix(uri)


__all__ = [
    "uri_prefix", "uri_join",
    "uri_writebytes", "uri_readbytes",
    "uri_list_uris"]
