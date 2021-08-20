#!/usr/bin/env python3
# coding: utf-8

__version__ = '0.3.1'

if __name__ == '__main__':
    print(__version__)

b32_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
b64_chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/'

b64_urlsafe_chars = \
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'


def random_string(length, chars=None):
    import random
    chars = chars or b32_chars
    return ''.join(random.choice(chars) for _ in range(length))


def remove_chars(text, chars):
    """
    :param text: (str)
    :param chars: (str or list) characters to be removed
    :return: (str)
    """
    return text.translate(dict.fromkeys(ord(c) for c in chars))


def remove_control_chars(text):
    return text.translate(dict.fromkeys(range(32)))


def remove_whitespaces(text):
    return ''.join(text.split())


def remove_newlines(text):
    # similar to VIM line join
    return ' '.join(text.splitlines())


def remove_emptylines(text):
    lines = text.splitlines(keepends=True)
    return ''.join(x for x in lines if x.strip())


def replace_newlines(text, nl='\n'):
    text = text.replace('\n\r', nl)
    text = text.replace('\r', nl)
    if nl != '\n':
        text = text.replace('\n', nl)
    return text


def dedup_spaces(text):
    import re
    return re.sub(r" {2,}", " ", text)


def proper_join(parts):
    import re
    regex = re.compile(r'\s$')
    _parts = []
    space = chr(32)
    for p in parts:
        if not p:
            continue
        if regex.search(p):
            _parts.append(p)
        else:
            _parts.append(p + space)
    return ''.join(_parts)
