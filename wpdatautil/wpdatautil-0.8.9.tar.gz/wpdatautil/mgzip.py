"""mgzip utilities."""
import logging
import math
import multiprocessing

import mgzip

from wpdatautil.humanfriendly import format_size
from wpdatautil.timeit import Timer

_COMPRESS_LEVEL = 6
_INVERSE_PI = 1 / math.pi
_CPU_COUNT_SCALER = (2 ** 30) ** _INVERSE_PI

log = logging.getLogger(__name__)


def _num_threads(num_bytes: int) -> int:
    """Return the number of threads to use for compression or decompression."""
    max_usable_cpu_count = multiprocessing.cpu_count() * 0.95
    return max(1, math.floor(min(_CPU_COUNT_SCALER, num_bytes ** _INVERSE_PI) * max_usable_cpu_count / _CPU_COUNT_SCALER))


def compress(uncompressed: bytes, description: str = "blob") -> bytes:
    """Compress the given bytes in parallel using `mgzip`.

    The number of compression threads is determined automatically based on the input size and the CPU count.
    """
    len_uncompressed = len(uncompressed)
    len_uncompressed_formatted = format_size(len_uncompressed)
    num_threads = _num_threads(len_uncompressed)
    log.debug(f"Compressing {description} from {len_uncompressed_formatted} using {num_threads} threads.")
    timer = Timer()
    compressed = mgzip.compress(uncompressed, compresslevel=_COMPRESS_LEVEL, thread=num_threads)
    log.debug(f"Compressed {description} to {format_size(len(compressed))} from {len_uncompressed_formatted} in {timer} using {num_threads} threads.")
    return compressed


def decompress(compressed: bytes) -> bytes:
    """Decompress the given bytes in parallel using `mgzip`.

    The number of decompression threads is determined automatically based on the input size and the CPU count.
    """
    return mgzip.decompress(compressed, thread=_num_threads(len(compressed)))
