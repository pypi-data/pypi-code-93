import struct
import math


def t01(data, length, pos):
    val = bytes(data[pos - 1])
    return val, pos + 1


def t02(data, length, pos):
    if length > 16:
        raise Exception
    return auto_unpack('>' + str(length) + 'B', data, pos)


def t04(data, length, pos):
    return auto_unpack(str(length) + 'c', data, pos)


def t05(data, length, pos):
    return False, pos


def t06(data, length, pos):
    def _decode_oid_component(enstr, epos):
        n = 0
        while True:
            oc, epos = auto_unpack('B', enstr, epos)
            oc = int(oc)
            n = n * 128 + (0x7F & oc)
            if octet < 128:
                break

        return n, epos

    oid = {}
    last = pos + length - 1
    if pos <= last:
        oid['smap'] = '\x06'
        octet, pos = auto_unpack('B', data, pos)
        octet = int(octet)
        oid[2] = math.fmod(octet, 40)
        octet = octet - oid[2]
        oid[1] = octet // 40

    while pos <= last:
        c, pos = _decode_oid_component(data, pos)
        oid[len(oid) + 1] = c
    return oid, pos


def t30(data, length, pos):
    seq = []
    spos = 1
    error = False
    sstr, new_pos = auto_unpack(str(length) + 'c', data, pos)
    while spos < length:
        try:
            new_seq, spos = decode(sstr, spos)
        except:
            new_seq = None
            error = True
        if not new_seq:
            break
        seq.append(new_seq)

    return seq, new_pos


def t0A(data, length, pos):
    return t02(data, length, pos)


decoder = {
    b'\x01': t01,
    b'\x02': t02,
    b'\x04': t04,
    b'\x05': t05,
    b'\x06': t06,
    b'\x30': t30,
    b'\x0A': t0A
}


def auto_unpack(fmt, data, pos=0):
    """自动计算unpack的大小并返回结果"""
    length = struct.calcsize(fmt)
    new_pos = pos + length
    result = struct.unpack(fmt, data[pos:new_pos])

    is_all_byte = True
    for item in result:
        if not isinstance(item, bytes):
            is_all_byte = False

    if is_all_byte:
        return bytes.join(b'', result), new_pos
    else:
        return *result, new_pos


def _decode_length(data, pos):
    length, new_pos = auto_unpack('B', data, pos)
    length = int(length)
    if length > 128:
        length = length - 128
        c = 0
        for i in range(length):
            c = c * 256
            n, new_pos = auto_unpack('B', data, new_pos)
            c = c + int(n)
        length = c
    return length, new_pos


def decode(data, pos=0):
    etype, new_pos = auto_unpack('c', data, pos)
    length, new_pos = _decode_length(data, new_pos)
    if etype in decoder:
        return decoder[etype](data, length, new_pos)
    else:
        return None, new_pos
