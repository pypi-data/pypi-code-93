'''This module evaluates an arithmetic expression input by the user, in
a supplied base. It uses the `Num` class of the `radix` module.'''

import re
from .radix import Num

SYMBOLS = ['+', '-', '/', '//', '*', '**', '%', '(', ')']


def expr(s, base=10, show=False):
    '''Evaluate the expression given by the user in the given base.

    Parameters -
    s - Expression string to be evaluated.
    base - The integer base of the numbers (should be between 2 and 36)
    show - Optionally print the expression that is input to `eval`.

    Note that using `eval` is safe here because only allowed operators
    are used and any other input is cast to the `Num` class. `eval` is
    not being used directly on the user input.
    '''
    tokens = tokenize(str(s))
    formatted_input = format_user_input(tokens, int(base))
    if show:
        print(formatted_input)
    return eval(formatted_input, {'Num': Num})


def tokenize(s):
    '''Get a list of operators and numbers, including floating point.'''

    return re.findall(r'(\w*[.]?\w+|//|\*\*|[()+*\-/])', s)


def format_user_input(tokens, base):
    '''Get a string formatted with allowed symbols and other input
    cast to the `Num` class.
    '''

    formatted_input = ''
    for token in tokens:
        if token in SYMBOLS:
            formatted_input += token
        else:
            formatted_token = f'Num(\'{token}\', {base})'
            formatted_input += formatted_token

    return formatted_input
