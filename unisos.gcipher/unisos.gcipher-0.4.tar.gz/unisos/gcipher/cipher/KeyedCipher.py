"""This module contains the KeyedCipher class and the InvalidKey exception."""


class KeyedCipher:

    """This is a simple base class for ciphers with keys.

    Subclasses of this class should do the following:

    1) Define and initialize an attribute named key.

    2) Define an attribute named keyDescription which holds a sentence 
       fragment describing what constitutes a valid key.

    3) Defined a method isValidKey(self, key) that returns True if the given
       key is valid.

    4) Possibly define a defaultKey attribute.

    5) Extend __setattr__ instead of overriding it.

    """

    def __setattr__(self, attribute, value):
        """Perform validation for the key attribute."""
        if attribute == "key":
            if not self.isValidKey(value):
                self.raiseInvalidKey(value)
        self.__dict__[attribute] = value

    def raiseInvalidKey(self, key):
        """Raise an InvalidKey exception for the given key."""
        raise InvalidKey(key, self.keyDescription)


class InvalidKey(ValueError):

    """An attempt was made to set an invalid key.
    
    The following attributes are used:

    key - This is the faulty key.

    keyDescription - This is a sentence fragment describing what is expected
    for the key.
    
    """

    def __init__(self, key, keyDescription):
        """Accept the arguments."""
        self.key = key
        self.keyDescription = keyDescription
        ValueError.__init__(self, key, keyDescription)
