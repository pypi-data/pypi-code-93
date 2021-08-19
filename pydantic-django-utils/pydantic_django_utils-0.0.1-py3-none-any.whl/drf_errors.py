from typing import Any, Dict, Sequence

from pydantic import ValidationError


def to_drf_error_details(exception: ValidationError) -> Dict[str, Any]:
    """
    Extract the arguments from a :class:`pydantic.ValidationError` and convert them to a
    dictionary whose format matches those used by the details for an error in Django
    Rest Framework.
    """
    drf_data: Dict[str, Any] = {}
    for error in exception.errors():
        _set_nested(drf_data, error["loc"], [error["msg"]])
    return drf_data


def _set_nested(data: Dict[str, Any], keys: Sequence[str], value: Any) -> None:
    """
    Set the value in a dictionary at the en of the nested keys, e.g.:

    >>> d = {"foo": {}}
    >>> _set_nested(d, ("foo", "bar"), None)
    >>> d
    {'foo': {'bar': None}}
    """
    for key in keys[:-1]:
        # stringify to be inline with DRF, e.g.
        # {"names": {"0": ["Must not contain numbers"]}}
        data = data.setdefault(str(key), {})
    data[keys[-1]] = value
