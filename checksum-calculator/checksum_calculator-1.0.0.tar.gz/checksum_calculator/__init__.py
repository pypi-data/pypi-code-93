from enum import Enum
from typing import *
from textwrap import wrap


class ChecksumType(Enum):
    XOR = 'xor'
    MOD256 = 'modulo 256'
    COMP_2S = '2s complement'


def get_checksum_type(line: str):
    """
    :param line:  The line that we would like to get the checksum type.

    :return:  The type of checksum the line could use. (Careful the function can return multiple result)
    """
    res = []
    if is_checksum8_xor(line):
        res.append(ChecksumType.XOR)
    if is_checksum8_mod256(line):
        res.append(ChecksumType.MOD256)
    if is_checksum8_2s_complement(line):
        res.append(ChecksumType.COMP_2S)
    return res


def compute_checksum8_xor(data: str) -> str:
    """
    :return:  The checksum computed with the method of 'or exclusive'.
    """
    xor = 0
    for value in wrap(data, 2):
        xor ^= int(value, base=16)
    return '%02X' % xor


def _sum_data(data: str) -> int:
    sum_ = 0
    for value in wrap(data, 2):
        sum_ += int(value, base=16)
    return sum_


def compute_checksum8_mod256(data: str) -> str:
    """
    :return:  The checksum computed with the method of 'sum and modulo 256'.
    """
    return '%02X' % (_sum_data(data) % 256)


def compute_checksum8_2s_complement(data: str) -> str:
    """
    :return:  The checksum computed with the method of '2s complement'.
    """
    return '%02X' % (-(_sum_data(data) % 256) & 0xFF)


_CHECKSUM_FUNCTION_TAB = {
    ChecksumType.XOR: compute_checksum8_xor,
    ChecksumType.MOD256: compute_checksum8_mod256,
    ChecksumType.COMP_2S: compute_checksum8_2s_complement
}
def compute_checksum(data: str, checksum_type: ChecksumType) -> str:
    """
    :param          data:  The data use for the computing.
    :param checksum_type:  The type of checksum to compute.

    :return:  The checksum computed with the method selected.
    """
    return _CHECKSUM_FUNCTION_TAB[checksum_type](data)


def _split_line(line: str, pos: int = 2) -> Tuple[str, str]:
    line = line.upper()
    return line[:-pos], line[-2:]


def is_checksum8_xor(line: str) -> bool:
    """
    :return:  True is the line have a checksum of 'or exclusive'
    """
    data, checksum = _split_line(line)
    return compute_checksum8_xor(data) == checksum


def is_checksum8_mod256(line: str) -> bool:
    """
    :return:  True is the line have a checksum of 'sum and modulo 256'
    """
    data, checksum = _split_line(line)
    return compute_checksum8_mod256(data) == checksum


def is_checksum8_2s_complement(line: str) -> bool:
    """
    :return:  True is the line have a checksum of '2s complement'
    """
    data, checksum = _split_line(line)
    return compute_checksum8_2s_complement(data) == checksum
