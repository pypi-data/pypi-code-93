from enum import Enum, Flag, auto, unique
from pprint import pprint
import re
from typing import Optional, Union


class FileSizeUnit(Enum):
    BYTE = 1
    KILO_BYTE = 1024
    MEGA_BYTE = 1048576
    GIGA_BYTE = 1073741824
    TERA_BYTE = 1099511627776
    PETA_BYTE = 1125899906842624

    def convert(self, amount: float) -> int:
        return round(amount * self.value)


class UnknownFileSizeUnit(Exception):
    def __init__(self, unit_string: str) -> None:
        self.unit_string = unit_string
        self.msg = f"{self.__class__.__name__}: Unit size {self.unit_string!r} is not a possible Unit."
        super().__init__(self.msg)


def make_reverse_dict(in_dict: dict):
    new_dict = {}
    for key, value in in_dict.items():
        if isinstance(value, (str, int, float)):
            new_dict[value] = key
        elif isinstance(value, (set, list, tuple)):
            for item in value:
                new_dict[item] = key
        else:
            raise NotImplementedError("values can only be string, integer, float, set, list, tuple")
    return new_dict


class FileSizeParser:
    unit_names = make_reverse_dict({FileSizeUnit.BYTE: {"b", "bs", "byte", "bytes"},
                                    FileSizeUnit.KILO_BYTE: {"kb", "kbs", "kilobyte", "kilobytes", "kilo_byte", "kilo_bytes", "kilob", "kilobs", "kilo_b", "kilo_bs", "kilo byte", "kilo bytes"},
                                    FileSizeUnit.MEGA_BYTE: {'mb', 'mbs', 'megabyte', 'megabytes', 'mega_byte', 'mega_bytes', 'mega byte', 'mega bytes', 'megab', 'megabs', 'mega_b', 'mega_bs'},
                                    FileSizeUnit.GIGA_BYTE: {'gb', 'gbs', 'gigabyte', 'gigabytes', 'giga_byte', 'giga_bytes', 'giga byte', 'giga bytes', 'gigab', 'gigabs', 'giga_b', 'giga_bs'},
                                    FileSizeUnit.TERA_BYTE: {'tb', 'tbs', 'terabyte', 'terabytes', 'tera_byte', 'tera_bytes', 'tera byte', 'tera bytes', 'terab', 'terabs', 'tera_b', 'tera_bs'},
                                    FileSizeUnit.PETA_BYTE: {'pb', 'pbs', 'petabyte', 'petabytes', 'peta_byte', 'peta_bytes', 'peta byte', 'peta bytes', 'petab', 'petabs', 'peta_b', 'peta_bs'}})

    parse_regex = re.compile(r"(?P<value>\d+(\,\d+)?)\s?(?P<unit>\w+(\s\w+)?)")

    @classmethod
    def parse(cls, data: Union[str, int]) -> int:
        if isinstance(data, (int, float)):
            return round(data)
        if data.isnumeric():
            return int(data)
        _out = 0
        for sub_match in cls.parse_regex.finditer(data):
            value = float(sub_match.group('value'))
            unit_name = sub_match.group('unit')
            if unit_name not in cls.unit_names:
                raise UnknownFileSizeUnit(unit_string=unit_name)

            _out += cls.unit_names.get(unit_name).convert(value)
        return _out


if __name__ == "__main__":
    pass
