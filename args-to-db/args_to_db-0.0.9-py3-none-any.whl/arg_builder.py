from .util import is_iterable

from itertools import product


def concat(command, arg):
    command = command.copy()
    return command + arg if is_iterable(arg) else command + [arg]


def add_command_arg(commands, args):
    return Arg([concat(cmd, arg) for cmd, arg in product(commands, args)])


class Arg(list):
    def __init__(self, options):
        if not is_iterable(options):
            options = [[options]]
        elif not is_iterable(options[0]):
            options = [[option] for option in options]

        list.__init__(self, options)

    def __add__(self, other):
        return add_command_arg(self, other)


def arg(options):
    return Arg(options)


def flag(flag, vary=True):
    assert isinstance(flag, str)
    
    options = [[flag]]
    if vary:
        options.insert(0, [])

    return Arg(options)


def option(identifier, values):
    assert isinstance(identifier, str)

    return Arg(identifier) + Arg(values)
