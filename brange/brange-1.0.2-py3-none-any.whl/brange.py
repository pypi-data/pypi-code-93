
def brange(a: int, b: int=None, step: int=1):
    """Returns a range object that increments or decrements
    in the right direction from a (inclusive) to b (exclusive).

    The specified step must be a positive integer
    or an empty range will always be returned.
    """

    if b is None:
        a, b = 0, a
    
    if a > b:
        step = -step
        
    return range(a, b, step)