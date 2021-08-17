from itertools import product

from .util import is_iterable


def concat(cmd_l, cmd_r):
    cmd_l = cmd_l.copy()
    return cmd_l + cmd_r if is_iterable(cmd_r) else cmd_l + [cmd_r]


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

    def __iadd__(self, other):
        return add_command_arg(self, other)


def arg(options):
    return Arg(options)


def flag(identifier, vary=True):
    assert isinstance(identifier, str)

    options = [[identifier]]
    if vary:
        options.insert(0, [])

    return Arg(options)


def option(identifier, values):
    assert isinstance(identifier, str)

    return Arg(identifier) + Arg(values)
