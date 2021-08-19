import sys
from typing import Any, Dict, List, Optional, Type, TypeVar

if sys.version_info >= (3, 8):
    from typing import get_origin
else:

    def get_origin(tp: Any) -> Optional[Any]:
        # very naive (but hopefully sufficient) implementation of
        # https://github.com/python/cpython/blob/8bdf12e99a3dc7ada5f85bba79c2a9eb9931f5b0/Lib/typing.py#L1844
        try:
            return tp.__origin__
        except AttributeError:
            return None


from django.http import QueryDict
from pydantic import BaseModel
from pydantic.fields import ModelField

_QueryDictModel = TypeVar("_QueryDictModel", bound="QueryDictModel")


class QueryDictModel(BaseModel):
    """
    A :class:`pydantic.BaseModel` whose :meth:`pydantic.BaseModel.parse_obj` can parse
    :class:`Django.http.QueryDict` via :func:`querydict_to_dict`

    >>> from django.http import QueryDict
    >>> class Model(QueryDictModel):
    ...     foo: int
    ...     bar: str
    >>> Model.parse_obj(QueryDict("foo=12&bar=hello"))
    Model(foo=12, bar='hello')
    """

    @classmethod
    def parse_obj(cls: Type["_QueryDictModel"], obj: Any) -> "_QueryDictModel":
        if isinstance(obj, QueryDict):
            obj = querydict_to_dict(obj, cls)
        return super().parse_obj(obj)


def querydict_to_dict(
    query_dict: QueryDict,
    model_class: Type[BaseModel],
) -> Dict[str, Any]:
    """
    Convert a :class:`Django.http.QueryDict` to a :class:`dict` under the constraints
    introduced on the types of fields of a :class:`pydantic.BaseModel`, i.e. by determining which
    of the fields should be lists versus single values by inspecting model's field
    types.
    """
    to_dict: Dict[str, Any] = {}
    model_fields = model_class.__fields__

    for key in query_dict.keys():
        if key in model_fields and _is_list_field(model_fields[key]):
            to_dict[key] = query_dict.getlist(key)
        else:
            to_dict[key] = query_dict.get(key)
    return to_dict


def _is_list_field(field: ModelField) -> bool:
    if sys.version_info >= (3, 7):
        return get_origin(field.outer_type_) == list
    else:
        return get_origin(field.outer_type_) == List
