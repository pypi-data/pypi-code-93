def all_are_none(*args) -> bool:
    """
    Return True if all args are None.
    """
    return all([arg is None for arg in args])


def none_are_none(*args) -> bool:
    """
    Return True if no args are None.
    """
    return not any([arg is None for arg in args])


def any_are_not_none(*args) -> bool:
    """
    Return True if any arg is not None.
    """
    return any([arg is not None for arg in args])


def any_are_none(*args) -> bool:
    """
    Return True if any arg is None.
    """
    return any([arg is None for arg in args])


def one_is_none(*args) -> bool:
    """
    Return True if exactly one arg is None.
    """
    return sum([arg is None for arg in args]) == 1


def one_is_not_none(*args) -> bool:
    """
    Return True if exactly one arg is not None.
    """
    return sum([arg is not None for arg in args]) == 1
