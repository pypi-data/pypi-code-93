import itertools


def tuplelize_array_entries(array):
    for i, element in enumerate(array):
        if isinstance(element, tuple):
            continue

        array[i] = (element, False)


def all_combinations_of_array(array):
    combs = []
    for count in range(len(array) + 1):
        combs += [list(tupl) for tupl in itertools.combinations(array, count)]
    return combs


def split_arguments(combinations):
    for i, args_tuples in enumerate(combinations):
        args = []
        for arg_tuple in args_tuples:

            if arg_tuple[1]:
                args += arg_tuple[0].split(' ')
            else:
                args += [arg_tuple[0]]

        combinations[i] = args


def all_combinations(*possible_args):
    array = possible_args[0] if len(possible_args) == 1 else possible_args
    array = list(array)

    tuplelize_array_entries(array)

    combinations = all_combinations_of_array(array)

    split_arguments(combinations)

    return combinations
