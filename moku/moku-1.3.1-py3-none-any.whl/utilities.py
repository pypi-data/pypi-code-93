from .exceptions import InvalidParameterRange
from .exceptions import MokuNotFound
from .finder import Finder


def validate_range(user_input, parameter_range):
    if user_input in parameter_range:
        return str(user_input)
    raise InvalidParameterRange(f"{user_input} is not in {parameter_range}")


def find_moku_by_serial(serial):
    result = Finder().find_all(timeout=10, filter=lambda x: x.serial == serial)
    if len(result):
        return result[0].ipv4_addr
    raise MokuNotFound()
