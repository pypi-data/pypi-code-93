import datetime
import decimal
import json

import arrow
from django.db import models
from ievv_opensource.utils.ievvbuildstatic.filepath import FilePathInterface


class Encoder(json.JSONEncoder):
    """
    Extends the default json.JSONEncoder with support for more types.

    Adds support for:

    - `datetime.datetime`
        - Serialized as ``{"__type__": "datetime", "value": "<iso datetime with timezone>"}``
    - `datetime.date`
        - Serialized as ``{"__type__": "date", "value": "<iso date YYYY-MM-DD>"}``
    - `datetime.time`
        - Serialized as ``{"__type__": "time", "value": "<str(timeobject)>"}``
    - `decimal.Decimal`
        - Serialized as ``{"__type__": "decimal", "value": "<str(decimalvalue)>"}``
    - Django model objects
        - Serialized as ``{"__type__": "djangomodel", "__model__": "someapp.SomeModel", "value": "<model object PK>"}``
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {
                '__type__': 'datetime',
                'value': arrow.get(obj).format()
            }
        elif isinstance(obj, datetime.date):
            return {
                '__type__': 'date',
                'value': obj.isoformat()
            }
        elif isinstance(obj, datetime.time):
            return {
                '__type__': 'time',
                'value': obj.isoformat()
            }
        elif isinstance(obj, decimal.Decimal):
            return {
                '__type__': 'decimal',
                'value': str(obj)
            }
        elif isinstance(obj, models.Model):
            return {
                '__type__': 'djangomodel',
                '__model__': f'{obj._meta.label}',
                'value': obj.pk
            }
        elif isinstance(obj, FilePathInterface):
            return obj.abspath
        return super().default(obj)


class Decoder(json.JSONDecoder):
    """
    Extends the default json.JSONDecoder with support for the types that :class:`.Encoder` supports.

    Note that even though :class:`.Encoder` supports Django models, we do not support
    looking up the actual database object. So decoding Django models just returns
    them with the same representation that they where encoded with (model + PK).
    """
    def __init__(self):
        super().__init__(object_hook=self.custom_object_hook)

    def custom_object_hook(self, d):
        if '__type__' not in d or 'value' not in d:
            return d
        _type = d['__type__']
        value = d['value']
        if _type == 'datetime':
            return arrow.get(value).datetime
        elif _type == 'date':
            return arrow.get(value).datetime.date()
        elif _type == 'time':
            return arrow.get(f'2000-01-01 {value}').datetime.time()
        elif _type == 'decimal':
            return decimal.Decimal(value)
        # NOTE: We do not support reverse lookup of django models in decoder!
        return d


def dumps(data, indent=None, sort_keys=False):
    """
    For most use-cases this is a drop in replacement for json.dumps()
    that just extends the supported datatypes with what :class:`.Encoder` supports.
    """
    return Encoder(indent=indent, sort_keys=sort_keys).encode(data)


def loads(data):
    """
    For most use-cases this is a drop in replacement for json.loads()
    that just extends the supported datatypes with what :class:`.Decoder` supports.
    """
    return Decoder().decode(data)
