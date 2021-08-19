'''
======================================================================
Generic wrapper for md5 generator
----------------------------------------------------------------------
'''
import json
from importlib import import_module
from hashlib import md5

from carte_blanche.find_path.find_path import walk
walk()

errors = import_module('carte_blanche.serializers.__errors__')


def hash(data, salt=None):
    hash_fn = md5()
    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)

    if not isinstance(data, bytes):
        data = data.encode('utf-8')

    hash_fn.update(data)
    hashed_data = hash_fn.hexdigest()

    if salt is not None:
        hash_fn.update(salt.encode('utf-8'))
        hashed_data = hash_fn.hexdigest()

    return hashed_data


if __name__ == '__main__':
    hashed = hash('123')
