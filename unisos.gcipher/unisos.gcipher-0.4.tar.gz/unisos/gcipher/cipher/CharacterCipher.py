"""This module contains the CharacterCipher class."""

from io import StringIO


class CharacterCipher:

    """This is a useful baseclass for character-oriented ciphers.

    Subclasses of this class do not need to implement encrypt or decrypt.
    Instead, they must implement encryptCharacter and decryptCharacter.

    """

    def encrypt(self, s):
        """Encrypt and return s."""
        return self._map(self.encryptCharacter, s)

    def decrypt(self, s):
        """Decrypt and return s."""
        return self._map(self.decryptCharacter, s)

    def _map(self, f, s):
        """Apply f to each character in s and return the new s.

        Use a cStringIO buffer.
        
        """
        buf = StringIO()
        for c in s:
            buf.write(f(c))
        return buf.getvalue()


# The following is for testing.
class _Test(CharacterCipher):
    def encryptCharacter(self, c): return 'z'
    def decryptCharacter(self, c): return 'a'


# Do some testing.
if __name__ == '__main__':
    cipher = _Test()
    assert cipher.encrypt("foo") == "zzz"
    assert cipher.decrypt("foo") == "aaa"
