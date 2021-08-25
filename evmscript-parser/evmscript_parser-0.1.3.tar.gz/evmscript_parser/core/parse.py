"""Parsing encoded EVM script."""
from typing import (
    Tuple
)

from .format import (
    EVMScript,
    OneCall,
    HEX_PREFIX,
    SPEC_ID_LENGTH, METHOD_ID_LENGTH, ADDRESS_LENGTH, CALL_DATA_LENGTH
)


def _parse_one_call(encoded_script: str, index: int) -> Tuple[int, OneCall]:
    """Parse one call segment and shift index."""
    address = encoded_script[index: index + ADDRESS_LENGTH]
    index += ADDRESS_LENGTH

    data_length = int(encoded_script[index:index + CALL_DATA_LENGTH], 16)
    index += CALL_DATA_LENGTH

    method_id = encoded_script[index: index + METHOD_ID_LENGTH]
    index += METHOD_ID_LENGTH

    offset = data_length * 2 - METHOD_ID_LENGTH
    call_data = encoded_script[index: index + offset]
    index += offset

    return index, OneCall(
        address, data_length, method_id, call_data
    )


def parse(encoded_script: str) -> EVMScript:
    """
    Parse encoded EVM script.

    :param encoded_script: str, encoded EVM script.
    :return: parsed script as instance of EVMScript object.
    """
    if encoded_script.startswith(HEX_PREFIX):
        encoded_script = encoded_script[len(HEX_PREFIX):]
    spec_id = encoded_script[:SPEC_ID_LENGTH]

    calls_data = []
    i = SPEC_ID_LENGTH
    while i < len(encoded_script):
        i, one_call = _parse_one_call(encoded_script, i)
        calls_data.append(one_call)

    return EVMScript(
        spec_id, calls_data
    )
