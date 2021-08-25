# -*- coding: utf-8 -*-
import decimal


def frequency(fre):
    """将'付息频率（月/次）' 换算为 '付息频率（单位：次/年）'
    """
    try:
        fre = 12 / fre
        # return round_up(fre, 2)
        return to_fixed(fre, num=2)
    except ZeroDivisionError:
        pass


def to_fixed(amount, num=6):
    """此函数主要为获取float格式的数字，按照常规的四舍五入的方式输出decimal格式的数字;
    example:
        to_fixed(3.88823, 2) --> 3.89
    """
    if amount is None:
        return
    fraction = decimal.Decimal("0.{}".format("0" * num))
    return decimal.Decimal(str(amount)).quantize(fraction, rounding="ROUND_HALF_UP")
