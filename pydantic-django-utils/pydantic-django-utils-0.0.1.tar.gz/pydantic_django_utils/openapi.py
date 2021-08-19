from typing import List, Type, cast

from pydantic import BaseModel
from pydantic.fields import ModelField
from typing_extensions import Literal, TypedDict

_In = Literal["query", "header", "path", "cookie"]

# Using the functional definition to avoid issues with the `in` keyword
ParameterDict = TypedDict(
    "ParameterDict",
    {
        "name": str,
        "in": _In,
        "description": str,
        "required": bool,
        "deprecated": bool,
        "allowEmptyValue": bool,
    },
    total=False,
)
ParameterDict.__doc__ = """\
A dictionary representing the fixed fields of an `OpenAPI parameter object
<https://swagger.io/specification/#parameter-object>`_

:ivar str name:
:ivar Literal["query", "header", "path", "cookie"] in:
:ivar str description:
:ivar bool required:
:ivar bool deprecated:
:ivar bool allowEmptyValue:
"""

_VALID_LOCATIONS = ("query", "header", "path", "cookie")


def pydantic_openapi_params(
    model_class: Type[BaseModel],
) -> List[ParameterDict]:
    """
    Build a List of :class:`ParameterDict` describing the fields of a :class:`pydantic.BaseModel`.
    By setting the fields according to:

    * :attr:`ParameterDict.name` via :attr:`pydantic.ModelField.name`
    * :attr:`ParameterDict.description` via :attr:`pydantic.ModelField.field_info.description`,
      defaults to ``""``
    * :attr:`ParameterDict.required` via :attr:`pydantic.ModelField.required`

    Some fields are set from values under :attr:`pydantic.BaseModel.field_info.extra`:

    * :attr:`ParameterDict.in` via ``location``, defaults to ``"query"``
    * :attr:`ParameterDict.deprecated` via ``deprecated``, defaults to ``False``
    * :attr:`ParameterDict.allowEmptyValue` via ``allowEmptyValue`` (only permitted if ``location``
      is ``"query"``). This key will not exist unless the field's location is ``"query"`` and in
      this case defaults to ``False``

    :raises ValueError: If any of the fields are complex types
    :raises ValueError: If ``location`` is not a value supported by :attr:`ParameterDict.in`
    :raises ValueError: If you try to set ``required`` to ``False`` on a field whose location is
        ``"path"``
    :raises ValueError: If you try to set ``allowEmptyValue`` on a field whose location is not
        ``"query"``
    """
    parameters: List[ParameterDict] = []

    for field in model_class.__fields__.values():
        if field.is_complex():
            raise ValueError("Only simple types allowed")
        else:
            parameters.append(_pydantic_field_to_parameter(field))

    return parameters


def _pydantic_field_to_parameter(field: ModelField) -> ParameterDict:
    location = field.field_info.extra.get("location", "query")
    if location not in _VALID_LOCATIONS:
        raise ValueError(f"location must be one of: {', '.join(_VALID_LOCATIONS)}")

    required = field.required
    if location == "path" and not required:
        raise ValueError("Path parameters must be required")

    field_extra = field.field_info.extra
    deprecated = field_extra.get("deprecated", False)

    args = {
        "name": field.name,
        "in": location,
        "description": field.field_info.description or "",
        "required": required,
        "deprecated": deprecated,
    }

    # allowEmptyValue only included for 'query' parameters
    allow_empty_value = field_extra.get("allowEmptyValue")
    if allow_empty_value is not None and location != "query":
        raise ValueError("allowEmptyValue only permitted for 'query' values")
    elif location == "query":
        if allow_empty_value is not None:
            args["allowEmptyValue"] = allow_empty_value
        else:
            args["allowEmptyValue"] = False

    return cast(ParameterDict, args)  # typing: ignore [misc]
