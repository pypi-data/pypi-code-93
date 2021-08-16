def is_iterable(obj):
    return isinstance(obj, (tuple, list))


def array_equal(left, right):
    if len(left) != len(right):
        return False

    for element in left:
        if element not in right:
            return False

    return True
