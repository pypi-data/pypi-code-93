'''
======================================================================
Generic wrapper for sha256 generator
----------------------------------------------------------------------
'''
import json
from importlib import import_module
from hashlib import sha256
import hmac

from carte_blanche.find_path.find_path import walk
walk()

errors = import_module('carte_blanche.serializers.__errors__')


def hash(data, salt=None):
    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)

    if not isinstance(data, bytes):
        data = data.encode('utf-8')

    hasher = hmac.new(data, digestmod=sha256)
    hashed_data = hasher.hexdigest()

    if salt is not None:
        hasher.update(salt.encode('utf-8'))
        hashed_data = hasher.hexdigest()

    return hashed_data


if __name__ == '__main__':
    from carte_blanche.serializers.salt import create
    salt = create()
    data = [1, 2, 3]
    hashed = hash(data, salt)
    print(hashed)
