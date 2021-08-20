"""This file contains the Gie class."""

from unisos.gcipher.cipher.CharacterCipher import CharacterCipher
from unisos.gcipher.cipher.Tools import apply_caseless, offset


class Gie(CharacterCipher):

    """This is a simple cipher that maps a..z -> z..a.

    It is named after my wife Gina-Marie who showed it to me.
    
    """

    def encryptCharacter(self, c):
        """Encrypt and return c."""
        if not c.isalpha():
            return c
        return apply_caseless(lambda c: chr(ord('z') - offset(c)), c)

    def decryptCharacter(self, c):
        """Decrypt and return c."""
        return self.encryptCharacter(c)


# Do some testing.
if __name__ == '__main__':
    cipher = Gie()
    assert cipher.encrypt("aAbB zZ") == "zZyY aA"
    assert cipher.decrypt("aAbB zZ") == "zZyY aA"
