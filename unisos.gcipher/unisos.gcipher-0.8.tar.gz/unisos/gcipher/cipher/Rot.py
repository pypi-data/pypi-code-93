"""This module contains the Rot class."""

from unisos.gcipher.cipher.CharacterCipher import CharacterCipher
from unisos.gcipher.cipher.KeyedCipher import KeyedCipher
from unisos.gcipher.cipher.Tools import LEN_ALPHABET, apply_caseless, offset, from_offset


class Rot(CharacterCipher, KeyedCipher):

    """This is the cipher used in Rot7, Rot13, Caesar's code, etc.

    This is a simple cipher that simply rotates the characters by an offset.
    For instance, ab..z -> b..za.

    The following attributes are used:

    key - What is the offset used in the rotation?  This will initially be set
    to defaultKey.

    keyDescription - This is a description of what constitutes a valid key.

    defaultKey - This is the default key.
    
    """

    keyDescription = "an integer in the range [0, 25]"
    defaultKey = 0

    def __init__(self):
        """Set key to defaultKey."""
        self.key = self.defaultKey

    def encryptCharacter(self, c):
        """Encrypt and return c."""
        return self._encryptCharacter(c, self.key)

    def decryptCharacter(self, c):
        """Decrypt and return c."""
        return self._encryptCharacter(c, -self.key)

    def _encryptCharacter(self, c, key):
        """Encrypt and return c.  Use the given key."""
        if not c.isalpha():
            return c
        return apply_caseless(
            lambda c: from_offset((offset(c) + key) % LEN_ALPHABET), c)

    def isValidKey(self, key):
        """Is key a a valid key?  See keyDescription."""
        return isinstance(key, type(0)) and 0 <= key and key < LEN_ALPHABET

    def __setattr__(self, attribute, value):
        """Extend KeyedCipher.__setattr__ to cast the key to an int."""
        strvalue = value
        if attribute == "key":
            try:
                value = int(value)
            except ValueError:
                self.raiseInvalidKey(strvalue)
        KeyedCipher.__setattr__(self, attribute, value)


# Do some testing.
if __name__ == '__main__':
    cipher = Rot()
    assert cipher.isValidKey(0)
    assert not cipher.isValidKey(-1)
    assert not cipher.isValidKey("a")
    cipher.key = "1"
    assert cipher.key == 1
    assert cipher.encrypt("aAzZ") == "bBaA"
    assert cipher.decrypt("bBaA") == "aAzZ"
