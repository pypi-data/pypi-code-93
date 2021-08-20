from bitfield import Bit


def IsBitOn(value, bit):
    if isinstance(bit, Bit):
        bit = bit.number

    res = (value & (1 << bit))
    if isinstance(res, int):
        return res
    return (value & (1 << bit))._value != 0


def IsBitOff(value, bit):
    return not IsBitOn(value, bit)


def TurnBitOn(value, bit):
    if isinstance(bit, Bit):
        bit = bit.number

    return value | (1 << bit)


def TurnBitOff(value, bit):
    if isinstance(bit, Bit):
        bit = bit.number

    return value & ~ (1 << bit)


def CopyBit(value, bit):
    if IsBitOn(value, bit):
        return TurnBitOn(value, bit)
    else:
        return TurnBitOff(value, bit)
