from numpy import around


def range_step(min_: int, max_: int, size: int) :
    return (max_ - min_) / size


def round(iterable_, decimals: int):
    return around(iterable_, decimals)
