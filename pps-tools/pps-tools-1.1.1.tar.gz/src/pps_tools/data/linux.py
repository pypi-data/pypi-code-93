import ctypes

from . import common


class Timespec(ctypes.Structure):
    """Mirror pps_ktime"""
    _fields_ = (
        ("tv_sec", ctypes.c_int64),
        ("tv_nsec", ctypes.c_int32),
        ("flags", ctypes.c_uint32),  # 0 = time specified, 1 otherwise
    )


class PpsTime(ctypes.Union):
    """Not in the kernel interface. For compatibility between FreeBSD and Linux code"""
    _fields_ = (
        ("tspec", Timespec),
        # ("ntpfp", NtpFp),
    )


class PpsInfo(ctypes.Structure):
    _fields_ = (
        ("assert_sequence", ctypes.c_uint32),
        ("clear_sequence", ctypes.c_uint32),
        ("assert_tu", PpsTime),
        ("clear_tu", PpsTime),
        ("current_mode", ctypes.c_int),
    )


class PpsFetchArgs(ctypes.Structure):
    _fields_ = (
        # No tsformat. Will be ignored in __init__.
        # ("tsformat", types.c_int),
        ("info", PpsInfo),
        ("timeout", Timespec),
    )


class PpsParams(ctypes.Structure):
    _fields_ = (
        ("api_version", ctypes.c_int),
        ("mode", ctypes.c_int),
        ("assert_off_tu", PpsTime),
        ("clear_off_tu", PpsTime),
    )


_DIR_SHIFT = 30  # May change based on arch. 30 for generic (e.g. ARM)
_IOC_V = 0
_IOC_W = 1 << _DIR_SHIFT
_IOC_R = 2 << _DIR_SHIFT
_IOC_RW = _IOC_R | _IOC_W


# Does not exist in Linux
PPS_IOC_CREATE = None
PPS_IOC_DESTROY = None

# The Linux PPS defines accidentally used pointers instead of structs for sizeof()
PPS_IOC_GETPARAMS = common.ioc(_IOC_R, 'p', 0xa1, ctypes.sizeof(ctypes.c_void_p))
PPS_IOC_SETPARAMS = common.ioc(_IOC_W, 'p', 0xa2, ctypes.sizeof(ctypes.c_void_p))
PPS_IOC_GETCAP = common.ioc(_IOC_R, 'p', 0xa3, ctypes.sizeof(ctypes.c_void_p))
PPS_IOC_FETCH = common.ioc(_IOC_RW, 'p', 0xa4, ctypes.sizeof(ctypes.c_void_p))
