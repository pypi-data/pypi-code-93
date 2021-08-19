import re
import typing

from extreme_parser.util import read_file


def parse_number(s, first=True) -> typing.Union[None, int, float, list]:
    def to_number(number_str):
        return float(number_str) if "." in s else int(number_str)

    numbers = re.findall(r"\d+\.\d+|\d+", s)
    if len(numbers) <= 0:
        return None
    if first:
        return to_number(numbers[0])
    else:
        return list(map(to_number, numbers))


def test_arg(cases, f):
    for no, case in enumerate(cases):
        f(read_file("../testdata/" + case["file"]), case["obj"])
        for k, attr_want in case["want"].items():
            attr_got = getattr(case["obj"], k)
            if attr_got != attr_want:
                print(f"case{no} {k} want {attr_want} got {attr_got}")
