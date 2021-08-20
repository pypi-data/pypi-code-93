"""This module contains the Vigenere class."""

from operator import add, sub

from unisos.gcipher.cipher.CharacterCipher import CharacterCipher
from unisos.gcipher.cipher.KeyedCipher import KeyedCipher
from unisos.gcipher.cipher.Tools import LEN_ALPHABET, apply_caseless, offset, from_offset


class Vigenere(CharacterCipher, KeyedCipher):

    """This is a Rot-like cipher that uses a private key.

    Basically, each letter is rotated by an amount that is a function of both
    its position in the file as well as the private key.

    The following attributes are used:

    key - This is the private key.
    keyDescription - This is a description of what constitutes a valid key.
    defaultKey - This is the default key.

    The following private variables are used:

    _keyIndex - This is a value in the range 0..len(key) that gets incremented 
    module len(key) for every ASCII character as that character is encrypted 
    or decrypted.
    
    """

    keyDescription = "one or more lowercase letters"
    defaultKey = "a"

    def __init__(self):
        """Set key to defaultKey."""
        self.key = self.defaultKey

    def encrypt(self, s):
        """Extend the base class's encrypt method to set _keyIndex to 0."""
        self._keyIndex = 0
        return CharacterCipher.encrypt(self, s)

    def decrypt(self, s):
        """Extend the base class's decrypt method to set _keyIndex to 0."""
        self._keyIndex = 0
        return CharacterCipher.decrypt(self, s)

    def encryptCharacter(self, c):
        """Encrypt and return c."""
        return self._cryptCharacter(c, add)

    def decryptCharacter(self, c):
        """Decrypt and return c."""
        return self._cryptCharacter(c, sub)

    def _cryptCharacter(self, c, f):
        """Take care of non-letters as well as the _keyIndex."""
        if not c.isalpha():
            return c
        ret = apply_caseless(self._cryptCharacterBackend, c, f)
        self._keyIndex = (self._keyIndex + 1) % len(self.key)
        return ret

    def _cryptCharacterBackend(self, c, f):
        """Actually do the encryption or decryption."""
        inputPart = offset(c)
        keyPart = offset(self.key[self._keyIndex])
        desiredOffset = f(inputPart, keyPart) % LEN_ALPHABET
        return from_offset(desiredOffset)

    def isValidKey(self, key):
        """Is key a a valid key?  See keyDescription."""
        return key.isalpha() and key.islower()


# Do some testing.
if __name__ == '__main__':
    cipher = Vigenere()
    assert cipher.isValidKey("abz")
    assert not cipher.isValidKey("ABC")
    assert not cipher.isValidKey(" ")
    cipher.key = "bad"
    assert cipher.key == "bad"
    assert cipher.encrypt("bad") == "cag"
    assert cipher.decrypt("cag") == "bad"
    cipher.key = "xyz"
    assert cipher.encrypt("bca") == "yaz"
    assert cipher.decrypt("yaz") == "bca"
