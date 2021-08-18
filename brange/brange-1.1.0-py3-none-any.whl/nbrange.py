import itertools

from .brange import brange



def nbrange(*dimensions: tuple[tuple[int]]):
    """N-dimensional implementation of brange
    
    dimensions: tuples containing a, b and step for every dimension
    """

    return itertools.product(*[brange(a, b, step) for a, b, step in dimensions])