def is_iterable(object):
    return isinstance(object, (tuple, list))

def array_equal(a, b):
    if len(a) != len(b):
        return False

    for element in a:
        if element not in b:
            return False

    return True