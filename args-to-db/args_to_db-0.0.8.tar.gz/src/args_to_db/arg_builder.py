from .util import is_iterable


def append_command(command, arg):
    copy = command.copy()
    return copy + arg if is_iterable(arg) else copy + [arg]


def add_commands_arg_option(left, right):
    new_commands = [append_command(cmd, arg) for arg in right for cmd in left]
    return Arg(new_commands)


class Arg(list):
    def __init__(self, options):
        if not is_iterable(options):
            options = [[options]]
        elif not is_iterable(options[0]):
            options = [[option] for option in options]

        list.__init__(self, options)

    def __add__(self, other):
        return add_commands_arg_option(self, other)
