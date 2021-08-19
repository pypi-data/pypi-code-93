"""humanfriendly utilities."""
import humanfriendly


def format_size(num_bytes: int) -> str:
    """Return the given number of bytes formatted as a human-readable size string using binary multiples.

    Examples
    --------
    0 -> "0 bytes"
    123456789 -> "117.74 MiB"
    3221225472 -> "3 GiB"

    """
    return humanfriendly.format_size(num_bytes, binary=True)
