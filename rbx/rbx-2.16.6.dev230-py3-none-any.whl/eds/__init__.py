from collections import namedtuple
from collections.abc import Mapping
import warnings

# Ignore Google Cloud warnings about using end user credentials.
warnings.filterwarnings('ignore', 'Your application has authenticated using end user credentials')


def namedtuple_with_defaults(typename, field_names, default_values=()):
    """Currently defaults for namedtuples are not supported right out the box.
    Python 3.7 does have support for this however until we are at that point this method
    serves the purpose.

    This method sets None to all specified `field_names`. However it does support specific
    defaults. e.g. default_values={name='test'}.
    """
    T = namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T


Aggregate = namedtuple('Aggregate', ['name', 'schema', 'table'])

Dimension = namedtuple_with_defaults(
    'Dimension',
    ['name', 'key', 'ancestor', 'model_based', 'key_field', 'id_fields', 'index_fields',
     'relatives', 'schema', 'tables'],
    default_values={'model_based': False, 'index_fields': ()}
)

Fact = namedtuple('Fact', ['name', 'schema'])

__all__ = ['Aggregate', 'Dimension', 'Fact']
