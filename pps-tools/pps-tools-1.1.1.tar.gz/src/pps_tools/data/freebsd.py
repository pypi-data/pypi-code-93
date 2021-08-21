import ctypes

from . import common


class NtpFp(ctypes.Structure):
    _fields = (
        ("integral", ctypes.c_uint),
        ("fractional", ctypes.c_uint),
    )


class Timespec(ctypes.Structure):
    _fields_ = (
        ("tv_sec", ctypes.c_int64),
        ("tv_nsec", ctypes.c_long),
    )


class PpsTime(ctypes.Union):
    _fields_ = (
        ("tspec", Timespec),
        ("ntpfp", NtpFp),
    )


class PpsInfo(ctypes.Structure):
    _fields_ = (
        ("assert_sequence", ctypes.c_uint),
        ("clear_sequence", ctypes.c_uint),
        ("assert_tu", PpsTime),
        ("clear_tu", PpsTime),
        ("current_mode", ctypes.c_int),
    )


class PpsFetchArgs(ctypes.Structure):
    _fields_ = (
        ("tsformat", ctypes.c_int),
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


_IOC_V = 0x20000000
_IOC_R = 0x40000000
_IOC_W = 0x80000000
_IOC_RW = _IOC_R | _IOC_W

PPS_IOC_CREATE = common.ioc(_IOC_V, '1', 1)
PPS_IOC_DESTROY = common.ioc(_IOC_V, '1', 2)
PPS_IOC_SETPARAMS = common.ioc(_IOC_W, '1', 3, ctypes.sizeof(PpsParams))
PPS_IOC_GETPARAMS = common.ioc(_IOC_R, '1', 4, ctypes.sizeof(PpsParams))
PPS_IOC_GETCAP = common.ioc(_IOC_R, '1', 5, ctypes.sizeof(ctypes.c_int))
PPS_IOC_FETCH = common.ioc(_IOC_RW, '1', 6, ctypes.sizeof(PpsFetchArgs))
