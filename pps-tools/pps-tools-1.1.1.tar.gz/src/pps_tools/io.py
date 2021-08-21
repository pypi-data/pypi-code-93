import ctypes
import fcntl
import os

from . import data


class PpsFile:
    """A Pythonic RFC2783 interface to PPS devices on the system.

    Python data types are taken and returned by the methods here, with conversion to underlying C data types as needed.
    The abstraction of these types is contained in the data submodule, as well as the per-platform IOCTL constants.

    Note that the code in here should avoid making platform introspection. Attempt to write the code in a way that
    works for all supported platforms.
    """
    def __init__(self, path):
        """Open and initialize the PPS device at the given path

        Args:
            path (str): Path to the PPS device
        """
        self._fd = os.open(path, os.O_RDWR)
        self._create()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _create(self):
        if data.PPS_IOC_CREATE is not None:
            fcntl.ioctl(self._fd, data.PPS_IOC_CREATE)

    def _destroy(self):
        if data.PPS_IOC_DESTROY is not None:
            fcntl.ioctl(self._fd, data.PPS_IOC_DESTROY)

    def close(self):
        """Destroy and close the underlying file descriptor."""
        self._destroy()
        os.close(self._fd)
        self._fd = None

    @property
    def closed(self):
        """Return True if the underlying file descriptor has been properly closed"""
        return self._fd is None

    def get_params(self):
        """Get the currently set parameters.

        The returned dictionary mirrors the arguments used for set_params.

        Returns:
            dict: A dictionary with assert_offset, clear_offset, api_version, and mode.
        """
        params = data.PpsParams()
        fcntl.ioctl(self._fd, data.PPS_IOC_GETPARAMS, params)
        return {
            "assert_offset": data.timespec_to_float(params.assert_off_tu),
            "clear_offset": data.timespec_to_float(params.clear_off_tu),
            "api_version": params.api_version,
            "mode": params.mode,
        }

    def set_params(self, assert_offset=0, clear_offset=0, api_version=1, mode=data.PPS_CAPTUREASSERT):
        """Set parameters for the PPS interface.

        The arguments mirror the dictionary keys in get_params().

        Args:
            assert_offset (float): Time offset to add to assert timestamps
            clear_offset (float): Time offset to add to clear timestamps
            api_version (int): Reported API version. Often has no bearing on the device.
            mode (int): Mode bits, as defined by data.PPS_* constants

        See also: get_cap()
        """
        assert_offset = data.PpsTime(tspec=data.float_to_timespec(assert_offset))
        clear_offset = data.PpsTime(tspec=data.float_to_timespec(clear_offset))
        params = data.PpsParams(
            api_version=api_version,
            mode=mode,
            assert_off_tu=assert_offset,
            clear_off_tu=clear_offset,
        )
        fcntl.ioctl(self._fd, data.PPS_IOC_SETPARAMS, params)

    def get_cap(self):
        """Obtain the interface mode bits.

        Returns:
           int: Mode bits in the data module to examine.
        """
        cap = ctypes.c_int()
        fcntl.ioctl(self._fd, data.PPS_IOC_GETCAP, cap)
        return cap.value

    def fetch(self, timeout=None):
        """Obtain the most recent timestamps captured for the PPS source.

        Args:
            timeout (float): Number of seconds to wait. None = indefinite.

        Returns:
            dict: assert_seq, clear_seq, assert_time, clear_time, and mode.
        """
        fetch_args = data.PpsFetchArgs(
            tsformat=data.PPS_TSFMT_TSPEC,
            timeout=data.float_to_timespec(timeout),
        )

        fcntl.ioctl(self._fd, data.PPS_IOC_FETCH, fetch_args)

        return {
            "assert_seq": fetch_args.info.assert_sequence,
            "clear_seq": fetch_args.info.clear_sequence,
            "assert_time": data.timespec_to_float(fetch_args.info.assert_tu),
            "clear_time": data.timespec_to_float(fetch_args.info.clear_tu),
            "mode": fetch_args.info.current_mode,
        }
