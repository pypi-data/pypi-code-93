import numpy as np

from .normal import normal
from .convective import convective


def generate_random_array(
    xyshape, ntimes, dtype="float32", generator=None, generator_kwargs=None
):
    """Generates an array of sample data chosen from a normal distribution

    Parameters
    ----------
    stats : tuple or list of tuples
        Array statistics in the format of [(mean,stddev)]
    xyshape : tuple
        Tuple of desired array shape

    Returns
    -------
    np.ndarray
        Array of random data
    """

    generator = normal if generator is None else generator
    generator_kwargs = {} if generator_kwargs is None else generator_kwargs

    result = generator(xyshape, ntimes, **generator_kwargs)

    return np.array(result).astype(dtype)
