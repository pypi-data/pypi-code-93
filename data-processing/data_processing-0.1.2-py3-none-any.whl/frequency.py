# -*- coding: utf-8 -*-

from .to_fixed import to_fixed


def frequency(fre):
    """将'付息频率（月/次）' 换算为 '付息频率（单位：次/年）'
    """
    try:
        fre = 12 / fre
        # return round_up(fre, 2)
        return to_fixed(fre, num=2)
    except ZeroDivisionError:
        pass


if __name__ == '__main__':
    print(frequency(3))
