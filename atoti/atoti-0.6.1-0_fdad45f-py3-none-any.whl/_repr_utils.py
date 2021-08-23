from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Union

_INDENTATION = "  "

ReprJson = Tuple[Any, Dict[str, Union[bool, str]]]


def _json_to_html(obj: Union[List[Any], Dict[str, Any]], indent: int = 0) -> str:
    return (
        _list_to_html(obj, indent)
        if isinstance(obj, list)
        else _dict_to_html(obj, indent)
    )


def _dict_to_html(dic: Dict[str, Any], indent: int = 0) -> str:
    pretty = f"{_INDENTATION * indent}<ul>\n"
    for key, value in dic.items():
        if isinstance(value, (dict, list)):
            pretty += f"{_INDENTATION * indent}<li>{key}\n"
            pretty += _json_to_html(value, indent + 1)
            pretty += f"{_INDENTATION * indent}</li>\n"
        else:
            pretty += f"{_INDENTATION * indent}<li>{key}: {value}</li>\n"
    return f"{pretty}{_INDENTATION * indent}</ul>\n"


def _list_to_html(lis: List[Any], indent: int = 0) -> str:
    pretty = f"{_INDENTATION * indent}<ol>\n"
    for value in lis:
        if isinstance(value, (dict, list)):
            pretty += (
                f"{_INDENTATION * indent}<li>{_json_to_html(value, indent + 1)}</li>\n"
            )
        else:
            pretty += f"{_INDENTATION * indent}<li>{value}</li>\n"
    return f"{pretty}{_INDENTATION * indent}</ol>"


class ReprJsonable(ABC):
    @abstractmethod
    def _repr_json_(self) -> ReprJson:
        """Return the JSON representation of this object."""

    def _repr_html_(self) -> str:
        """Return the HTML representation of this object."""
        repr_json = self._repr_json_()
        metadata = repr_json[1]
        if "root" in metadata:
            obj = {str(repr_json[1]["root"]): repr_json[0]}
        else:
            obj = repr_json[0]
        return _json_to_html(obj)
