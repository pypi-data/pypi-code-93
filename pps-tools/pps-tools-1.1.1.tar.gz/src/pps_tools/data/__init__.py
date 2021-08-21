import sys

# Flatten, based on platform
if sys.platform.startswith("freebsd"):
    from .freebsd import *
elif sys.platform.startswith("linux"):
    from .linux import *
else:
    raise ImportError("Unsupported platform: " + sys.platform)

from .common import *

NSECS_PER_SEC = 1000000000


def timespec_to_float(time):
    """Translate a Timespec structure to a floating point time value in seconds"""
    sec = time.tspec.tv_sec
    nsec = time.tspec.tv_nsec
    return sec + (nsec / NSECS_PER_SEC)


def float_to_timespec(time):
    """Translate a floating point time value in seconds to a Timespec structure"""
    # Indicate no time specified by default
    flags = 1  # For Linux. Not serialized in FreeBSD.
    sec = -1  # For FreeBSD. Does not work in Linux.
    nsec = 0

    if time is not None:
        flags = 0
        sec = int(time)
        nsec = int((time - sec) * NSECS_PER_SEC)

    return Timespec(tv_sec=sec, tv_nsec=nsec, flags=flags)


def cap_to_dict(cap):
    """Translate the capability integer into a capability dict.

    Args:
        cap (int): Capabilities integer from get_cap()

    Returns:
        dict: Dictionary of capability name to a 1/0 integer
    """
    return {name: int(bool(cap & bv)) for bv, name in MODE_BITS}
