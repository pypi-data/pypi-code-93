'''
======================================================================
Generic wrapper for generating salts
----------------------------------------------------------------------
'''
import secrets
from importlib import import_module


from carte_blanche_utils.find_path.find_path import walk
walk()

errors = import_module('carte_blanche_utils.serializers.__errors__')


def create():

    salt = str(secrets.randbits(128))

    return salt


if __name__ == '__main__':
    print(create())
