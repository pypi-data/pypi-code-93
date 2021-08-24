"""Module containing string-related utility functions."""

from __future__ import annotations
import math


__all__ = [
    # Function exports
    'class_repr',
    'digitlen',
    'special_chars_to_words',
    'special_words_to_chars',
]


_SPECIAL_CHAR_TO_WORDS = {
    ' ': 'SPACE',
    '!': 'EXCLAMATION',
    '#': 'HASH',
    '$': 'DOLLAR',
    '%': 'PERCENT',
    '&': 'AMPERSAND',
    '*': 'ASTERISK',
    '+': 'PLUS',
    ',': 'COMMA',
    '-': 'HYPHEN',
    '.': 'DOT',
    '/': 'SLASH',
    ':': 'COLON',
    ';': 'SEMICOLON',
    '?': 'QUESTION',
    '@': 'AT',
    '\\': 'BACKSLASH',
    '_': 'UNDERSCORE',
}


def class_repr(obj: object, properties: list[str]):
    return (f'{obj.__class__.__name__}(' +
            ', '.join([f'{p}={getattr(obj, p)!r}' for p in properties]) +
            ')')


def special_chars_to_words(value: str) -> str:
    """Replace special characters with token words enclosed with brackets."""
    result = str(value)
    for special_char, special_word in _SPECIAL_CHAR_TO_WORDS.items():
        result = result.replace(special_char, f'[{special_word}]')

    return result


def special_words_to_chars(value: str) -> str:
    """Replace bracket-enclosed token words with special characters."""
    result = str(value)
    for special_char, special_word in _SPECIAL_CHAR_TO_WORDS.items():
        result = result.replace(f'[{special_word}]', special_char)

    return result


def digitlen(n: int) -> int:
    """Returns the length of a number.

    Arguments:
        n: The input number.

    Return:
        The length of the input number.
    """
    try:
        n = int(n)
    except TypeError:
        return 0

    if n > 0:
        return int(math.log10(n))+ 1

    if n == 0:
        return 1

    # +1 if you don't count the '-'
    return int(math.log10(-n)) + 2
