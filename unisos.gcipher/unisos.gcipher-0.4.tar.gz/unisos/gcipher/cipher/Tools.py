"""This is a collection of tools for implementing ASCII based ciphers."""


LEN_ALPHABET = 26

def apply_caseless(f, c, *args, **kargs):
    """Apply the function f to the character c caselessly.

    The function f will receive a lower case version of c, but the return 
    value of this function will have the same case as the original c did.

    """
    ret = f(c.lower(), *args, **kargs)
    if c.isupper():
        ret = ret.upper()
    return ret

def offset(c):
    """Get the offset of c from 'a'."""
    return ord(c) - ord('a')

def from_offset(offset):
    """Given an offset from 'a', return the character."""
    return chr(ord('a') + offset)


# Do some testing.
if __name__ == '__main__':
    assert apply_caseless(lambda c: 'a', 'b') == 'a'
    assert apply_caseless(lambda c: 'a', 'B') == 'A'
    assert offset('a') == 0
    assert offset('z') == LEN_ALPHABET - 1
    assert from_offset(0) == 'a'
    assert from_offset(LEN_ALPHABET - 1) == 'z'
