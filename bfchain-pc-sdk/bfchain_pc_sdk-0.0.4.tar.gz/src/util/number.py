# -*- coding: utf-8 -*-
import ctypes


def u8(val):
    return ctypes.c_ubyte(val).value


def u16(val):
    return ctypes.c_uint16(val).value


def u32(val):
    return ctypes.c_ulong(val).value


def u64(val):
    return ctypes.c_ulonglong(val).value


def i64(val):
    return ctypes.c_longlong(val).value


def byte_to_hex(byte_):
    """
    显示十进制字节数组转十六进制字符串
    :param byte_: 字节数组
    :return: 字符串
    """
    result = ''
    for i in range(len(byte_)):
        result += hex(u8(byte_[i]))[2:] if len(hex(u8(byte_[i]))[2:]) == 2 else '0' + hex(u8(byte_[i]))[2:]
    return result


def hex_to_byte(hex_str, has_prefix=True):
    """
    显示十六进制字符串转十进制字节数组
    :param hex_str:
    :param has_prefix:
    :return:
    """
    if len(hex_str) % 2 != 0:
        raise ValueError("字符串长度不是2的倍数")
    # 如果包含0x则每4位进行截断，否则每2位截断
    cut = 4 if has_prefix else 2
    byte_length = len(hex_str) / cut
    byte_ = [0] * byte_length
    for i in range(byte_length):
        byte_[i] = int(hex_str[i * cut:(i + 1) * cut], 16)
    return byte_
