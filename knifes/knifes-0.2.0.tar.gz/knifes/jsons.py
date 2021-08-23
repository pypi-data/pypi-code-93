import json
import datetime
from . import times
import decimal
import uuid


# object encode
class ObjectEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return times.to_timestamp(o, unit='millisecond')
        elif isinstance(o, (decimal.Decimal, uuid.UUID)):
            return str(o)
        elif isinstance(o, set):
            return list(o)
        else:
            return o.__dict__


# obj to json
def to_json(obj):
    return json.dumps(obj, cls=ObjectEncoder)