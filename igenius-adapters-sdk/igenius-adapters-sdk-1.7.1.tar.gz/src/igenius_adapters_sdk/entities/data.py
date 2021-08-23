import abc
import hashlib
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, PrivateAttr, validator
from typing_extensions import Literal

from igenius_adapters_sdk.entities import attribute, numeric_binning, uri

__all__ = [
    "AggregationAttribute",
    "BinningAttribute",
    "ProjectionAttribute",
]


class OrderByDirection(str, Enum):
    DESC = "desc"
    ASC = "asc"


class AliasableAttribute(BaseModel):
    alias: str
    _shortened_alias: str = PrivateAttr()
    _original_alias: str = PrivateAttr()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        object.__setattr__(self, "_original_alias", self.alias)
        object.__setattr__(self, "_shortened_alias", str(hashlib.md5(self.alias.encode("utf-8")).hexdigest()))

    def switch_to_shortened_alias(self):
        self.alias = self._shortened_alias

    def get_original_alias(self):
        return self._original_alias

    def has_been_shortened(self):
        return self.alias != self._original_alias


class StaticValueAttribute(AliasableAttribute):
    value: str
    default_bin_interpolation: Optional[Any]


class BaseAttribute(AliasableAttribute, abc.ABC):
    attribute_uri: uri.AttributeUri


class ProjectionAttribute(BaseAttribute):
    pass


class OrderByAttribute(AliasableAttribute):
    direction: OrderByDirection = OrderByDirection.ASC


class FunctionUri(BaseModel):
    function_type: Literal["group_by", "aggregation"]
    function_uid: str
    function_params: Optional[Union[numeric_binning.BinningRules, attribute.StaticTypes]]

    @validator("function_uid")
    def check_uid_existence(cls, v, values):
        if "function_type" in values:
            if values["function_type"] == "group_by":
                attribute.GroupByFunction.from_uid(v)
            if values["function_type"] == "aggregation":
                attribute.AggregationFunction.from_uid(v)
        return v

    @validator("function_params")
    def check_binning_rules_consistency(cls, v, values):
        if v and values["function_uid"] == attribute.GroupByFunction.NUMERIC_BINNING.uid:
            if not isinstance(v, numeric_binning.BinningRules):
                raise ValueError("function_params does not contain BinningRules")
        return v


class AggregationAttribute(BaseAttribute):
    function_uri: FunctionUri
    default_bin_interpolation: Optional[Any]

    @validator("function_uri")
    def check_type(cls, v):
        if v and v.function_type and v.function_type != "aggregation":
            raise ValueError("Function type should be aggregation")
        return v


class BinningAttribute(BaseAttribute):
    function_uri: FunctionUri

    @validator("function_uri")
    def check_type(cls, v):
        if v and v.function_type and v.function_type != "group_by":
            raise ValueError("Function type should be group_by")
        return v
