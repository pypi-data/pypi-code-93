# -*- coding: utf-8 -*-

import decimal


def to_fixed(amount, num=6):
    """此函数主要为获取float格式的数字，按照常规的四舍五入的方式输出decimal格式的数字;
    example:
        to_fixed(3.88823, 2) --> 3.89
    """
    if amount is None:
        return
    fraction = decimal.Decimal("0.{}".format("0" * num))
    return decimal.Decimal(str(amount)).quantize(fraction, rounding="ROUND_HALF_UP")


if __name__ == '__main__':
    print(to_fixed(3.888239, 2))
