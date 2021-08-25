"""pandas base64 utilities."""
from hashlib import shake_128

import pandas as pd
from pybase64 import urlsafe_b64encode  # Benchmarked to be slightly faster than Python's base64 module over millions of rows.


def series_to_str_id(pd_series: pd.Series, /) -> str:
    """Return a reproducibly random string ID of 128 bits which is 16 bytes which is 24 urlsafe base64 characters.

    Usage pattern:
    >>> assert len(df.drop_duplicates()) <= 2 ** 64
    >>> df['xyz_id'] = df.apply(series_to_str_id, axis="columns").astype("string")

    In practice it is more efficient to apply the function only to unique rows, and then merge the results.
    """
    # Notes:
    #  A cache is intentionally not used because the function is expected to be called exactly once for each key.
    #  A 50% probability of a collision is at 2**64 inputs.
    #  A digest of length 32 must not be used because it will produce 44 base64 characters which could subsequently undesirably get mutated by Datavant Link.

    # Verbose version:
    # seed = str(tuple(pd_series)).encode()  # str(tuple(pd_series)) (without any index) is required for reproducibility.
    # hasher = shake_128(seed)
    # digest = hasher.digest(16)  # pylint: disable=too-many-function-args
    # id_ = urlsafe_b64encode(digest).decode()
    # return id_

    return urlsafe_b64encode(shake_128(str(tuple(pd_series)).encode()).digest(16)).decode()  # pylint: disable=too-many-function-args
