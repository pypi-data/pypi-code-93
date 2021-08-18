from itertools import product

from .util import _is_iterable


def _concat(cmd_l, cmd_r):
    cmd_l = cmd_l.copy()
    return cmd_l + cmd_r if _is_iterable(cmd_r) else cmd_l + [cmd_r]


def _add_arg(arg_l, arg_r):
    return _Arg([
        _concat(cmd_l, cmd_r) for cmd_l, cmd_r in product(arg_l, arg_r)
    ])


class _Arg(list):
    def __init__(self, options):
        if not _is_iterable(options):
            assert isinstance(options, str)
            options = [[options]]

        elif not _is_iterable(options[0]):
            for opt in options:
                assert isinstance(opt, str)

            options = [[option] for option in options]

        list.__init__(self, options)

    def __add__(self, other):
        return _add_arg(self, other)

    def __iadd__(self, other):
        return _add_arg(self, other)

    def __mul__(self, n):
        raise NotImplementedError()

    def __rmul__(self, n):
        raise NotImplementedError()

    def __imul__(self, n):
        raise NotImplementedError()


def arg(options):
    """Creates a single or multiple value argument object for command
       contruction.

    Args:
        options (str, list): Command or list of commands

    Returns:
        _Arg: 2D array of commands.
    """
    is_list = isinstance(options, list)
    is_str = isinstance(options, str)

    assert is_list or is_str, 'Passed argument must be a list or string.'
    if is_list:
        assert all(isinstance(option, str) for option in options), \
            'All argument options must be strings.'

    return _Arg(options)


def flag(identifier, vary=True):
    """Creates a flag object for command construction.

    Args:
        identifier (str): string of the actual flag to be added to the command
        vary (bool, optional): Wether this flag is to be understood as an
            optional one. Defaults to True.

    Returns:
        _Arg: 2D array of commands.
    """
    assert isinstance(identifier, str), 'Flag identifier must be of type str.'
    assert isinstance(vary, bool), 'Vary argument takes a bool as parameter.'

    options = [[identifier]]
    if vary:
        options.insert(0, [])

    return _Arg(options)


def option(identifier, values):
    """Creates a option object for command construction.

    Args:
        identifier (str): String of the option identifier.
        values (list): Possible values of the option.

    Returns:
        _Arg: 2D array of commands.
    """
    assert isinstance(identifier, str), 'Identifier must be of type str.'

    is_list = isinstance(values, list)
    is_str = isinstance(values, str)
    assert is_list or is_str, 'Values type must be either str or list.'
    if is_list:
        assert all(isinstance(option, str) for option in values), \
            'All possible values must be of type str.'

    return _Arg(identifier) + _Arg(values)


# import itertools

# def tuplelize_array_entries(array):
#     for i, element in enumerate(array):
#         if isinstance(element, tuple):
#             continue

#         array[i] = (element, False)


# def all_combinations_of_array(array):
#     combs = []
#     for count in range(len(array) + 1):
#        combs += [list(tupl) for tupl in itertools.combinations(array, count)]
#     return combs


# def split_arguments(combinations):
#     for i, args_tuples in enumerate(combinations):
#         args = []
#         for arg_tuple in args_tuples:

#             if arg_tuple[1]:
#                 args += arg_tuple[0].split(' ')
#             else:
#                 args += [arg_tuple[0]]

#         combinations[i] = args


# def all_combinations(*possible_args):
#     array = possible_args[0] if len(possible_args) == 1 else possible_args
#     array = list(array)

#     tuplelize_array_entries(array)

#     combinations = all_combinations_of_array(array)

#     split_arguments(combinations)

#     return combinations
