"""
util.py 工具包
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/2/21 11:52 AM
"""


class Units:
    """
    单位转换
    """

    B = 'B'
    KB = 'KB'
    KiB = 'KiB'
    MB = 'MB'
    MiB = 'MiB'
    GB = 'GB'
    GiB = 'GiB'
    TB = 'TB'
    TiB = 'TiB'
    PB = 'PB'
    PiB = 'PiB'
    EB = 'EB'
    EiB = 'EiB'
    ZB = 'ZB'
    ZiB = 'ZiB'
    YB = 'YB'
    YiB = 'YiB'
    BB = 'BB'
    BiB = 'BiB'
    NB = 'NB'
    NiB = 'NiB'
    DB = 'DB'
    DiB = 'DiB'

    b_values = {B: 1}

    __default_format = "%.{num}f"

    b_units = [B]
    kb_units = [KB, MB, GB, TB, PB, EB, ZB, YB, BB, NB, DB]
    kib_units = [KiB, MiB, GiB, TiB, PiB, EiB, ZiB, YiB, BiB, NiB, DiB]

    @classmethod
    def get_values(cls):
        if len(cls.b_values) <= 1:
            for index, unit in enumerate(cls.kib_units):
                cls.b_values[unit] = 1 << (index + 1) * 10
            for index, unit in enumerate(cls.kb_units):
                cls.b_values[unit] = 10 ** ((index + 1) * 3)
        return cls.b_values

    @classmethod
    def get(cls, key):
        return cls.get_values().get(key)

    @classmethod
    def convert(cls, string_value: str, unit: str = B, decimals: int = 2) -> tuple:
        """
        单位转换
        :param string_value: eg： 1MiB
        :param unit: 要转换的单位 eg: Units.KiB
        :param decimals: 需要保留的小数位
        :return: (1024.00, 'KiB')
        """

        byte_value = cls.convert_to_byte(string_value=string_value)
        data_format = cls.__default_format.format(num=decimals)
        return (data_format % (byte_value / cls.get(unit))), unit

    @classmethod
    def convert_to_byte(cls, string_value: str) -> float:
        """
        带单位字符串转换为字节
        :param string_value: eg： 1KiB
        :return: eg: 1024.0
        """

        __value, __unit = cls.analysis_unit_string(string_value)

        return __value * cls.get(__unit)

    @classmethod
    def analysis_unit_string(cls, string_value: str) -> tuple:
        """
        解析带有单位的字符串
        :param string_value: eg： 100.5GiB
        :return: eg: (100.5,'GiB')
        """

        __units = cls.kib_units + cls.kb_units + cls.b_units
        __units = {i: i.upper() for i in __units}
        for __unit, __unit_upper in __units.items():
            if string_value.upper().endswith(__unit_upper):
                return float(string_value[:-len(__unit)]), __unit
        return float(string_value), cls.B
