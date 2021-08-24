"""Helper functions."""

from typing import Dict
from typing import Mapping
from typing import TypeVar

__all__ = [
    'tensor_to_op',
    'op_to_tensor',
    'strip_zero_suffix',
    'add_zero_suffix',
]

# Disabled error is: Class name "T" doesn't conform to PascalCase naming style (invalid-name)
T = TypeVar('T')  # pylint: disable=C0103

_SUFFIX = ':0'


def strip_zero_suffix(tensor_name: str) -> str:
    """Strip zero suffix.

    :param tensor_name: tensor name
    :return: op name
    """
    assert tensor_name.endswith(_SUFFIX)
    return tensor_name[:-len(_SUFFIX)]


def add_zero_suffix(op_name: str) -> str:
    """Add zero suffix.

    :param op_name: op name
    :return: tensor name
    """
    return op_name + _SUFFIX


def tensor_to_op(tensor_mapping: Mapping[str, T]) -> Dict[str, T]:
    """Apply strip_zero_suffix to input mapping.

    :param tensor_mapping: input mapping
    :return: output dict
    """
    return {strip_zero_suffix(name): array for name, array in tensor_mapping.items()}


def op_to_tensor(tensor_mapping: Mapping[str, T]) -> Dict[str, T]:
    """Apply add_zero_suffix to input mapping.

    :param tensor_mapping: input mapping
    :return: output dict
    """
    return {add_zero_suffix(name): array for name, array in tensor_mapping.items()}
