from base64 import b64encode
import datetime
from hashlib import sha256
import hmac

import simplejson as json


def datetime_or_default_handler(*args):
    if isinstance(args[1], datetime.datetime) or isinstance(args[1], datetime.date):
        return args[1].isoformat()
    return f'Unconvertable Type {args[1].__name__}'


json.JSONEncoder.default = datetime_or_default_handler


class Signer:
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def sign(self, payload):
        data = self.sanitize(payload)
        computed_sig = hmac.new(
            self.secret_key.encode('utf-8'),
            msg=data,
            digestmod=sha256,
        ).digest()
        signature = b64encode(computed_sig).decode()
        return signature

    def verify(self, *, signature, payload):
        return signature == self.sign(payload)

    def sanitize(self, data):
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            pass
        else:
            data = json.dumps(data)
        return data.encode('utf-8')
