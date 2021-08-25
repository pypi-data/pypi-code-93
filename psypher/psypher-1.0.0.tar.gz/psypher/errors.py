'''
psypher.errors - Module for all psypher exceptions.
'''

from . import Error

class InvalidKeyData(Error):
    'Invalid key data when importing key.'

class UnexportableKey(Error):
    'The key is not suitable for raw export.'

class ForbiddenInCacheMode(Error):
    'Operation is not available when cache is enabled.'

class MissingRemoteKey(Error):
    'Remote key not received yet.'

class InvalidCiphertext(Error):
    'Ciphertext is invalid.'