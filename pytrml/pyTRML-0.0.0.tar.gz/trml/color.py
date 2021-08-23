from colorama.ansi import Fore, Back, Style
from .lexer import parse


def format(string):
    tree = parse(string)
    for tag, attrs in tree.items():
        color_head = exchange_text_attrs(attrs)
        string = string.replace(tag, color_head)
    return string


def exchange_text_attrs(attrs):
    color_head = ''
    if color := attrs.get('color', None):
        if color.upper() in dir(Fore):
            color_head += getattr(Fore, color.upper())

    if back := attrs.get('on', None):
        if back.upper() in dir(Back):
            color_head += getattr(Back, back.upper())

    if style := attrs.get('style', None):
        if style.upper() in dir(Style):
            color_head += getattr(Style, style.upper())

    if reset := attrs.get('auto_reset', 'true'):
        if reset.lower() in ['false', 'true']:
            if reset.lower() == 'true' and len(list(attrs.keys())) <= 1:
                color_head += Style.RESET_ALL

    return color_head

