import json
import pathlib
import numpy as np


def numpy_encoder(obj):
    # See https://stackoverflow.com/a/52604722/2117197
    if type(obj).__module__ == np.__name__:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj.item()

    raise TypeError('Unknown type:', type(obj))


def _compound_defaults(*defaults):

    def new_default(obj):
        for default in defaults:
            try:
                return default(obj)
            except TypeError:
                pass

        raise TypeError('Unknown type:', type(obj))

    return new_default


def _set_default_arg(kwargs):
    if 'default' in kwargs:
        kwargs['default'] = _compound_defaults(kwargs['default'], numpy_encoder)
    else:
        kwargs['default'] = numpy_encoder


def json_dumps(obj, *args, **kwargs):
    _set_default_arg(kwargs)
    return json.dumps(obj, *args, **kwargs)


def json_dump(obj, fp, *args, **kwargs):
    _set_default_arg(kwargs)
    if isinstance(fp, (str, pathlib.Path)):
        with open(fp, 'w') as file_descriptor:
            return json.dump(obj, file_descriptor, *args, **kwargs)
    return json.dump(obj, fp, *args, **kwargs)
