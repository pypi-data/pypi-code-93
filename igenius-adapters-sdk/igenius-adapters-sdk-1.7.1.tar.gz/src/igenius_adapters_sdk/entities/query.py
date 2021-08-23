import abc
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator

from igenius_adapters_sdk.entities import data, params, uri


class JoinType(str, Enum):
    INNER = "inner"
    LEFT_OUTER = "left-outer"
    RIGHT_OUTER = "right-outer"


class CriteriaType(str, Enum):
    AND = "and"
    OR = "or"


class JoinPart(BaseModel):
    from_: "From"
    on: uri.AttributeUri


class Join(BaseModel):
    left: JoinPart
    right: JoinPart
    type: JoinType  # noqa: A003


From = Union[uri.CollectionUri, Join]
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/#self-referencing-models
JoinPart.update_forward_refs()


class Expression(BaseModel):
    attribute_uri: uri.AttributeUri
    operator: str
    value: Any

    @validator("operator")
    def check_uid_existance(cls, v):
        params.ParamOperation.from_uid(v)
        return v

    @validator("value")
    def validate_operation_schema(cls, v, values):
        if "operator" in values:
            schema = params.ParamOperation.from_uid(values["operator"]).properties_schema
            operation_schema = params.OperationSchemas.from_jsonschema(schema)
            if v is None:
                v = {}
            if not isinstance(v, dict):
                key = next(iter(params.OperationPropertiesSchema.SingleValue.__fields__))
                v = {key: v}
            return operation_schema.model(**v).dict()
        return v


class MultiExpression(BaseModel):
    criteria: CriteriaType
    expressions: List[Union["MultiExpression", Expression]]


WhereExpression = Union[MultiExpression, Expression]
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/#self-referencing-models
MultiExpression.update_forward_refs()


class BaseQuery(BaseModel, abc.ABC):
    from_: From
    where: Optional[WhereExpression]
    order_by: Optional[List[data.OrderByAttribute]]
    limit: int = Field(None, ge=0)
    offset: int = Field(None, ge=0)


class SelectQuery(BaseQuery):
    attributes: List[Union[data.ProjectionAttribute, data.StaticValueAttribute]]
    distinct: bool = False


class AggregationQuery(BaseQuery):
    aggregations: List[Union[data.AggregationAttribute, data.StaticValueAttribute]]


class GroupByQuery(BaseQuery):
    aggregations: List[Union[data.AggregationAttribute, data.StaticValueAttribute]]
    groups: List[data.BinningAttribute]
    bin_interpolation: Optional[bool] = None

    @root_validator
    def bin_interpolation_flag_validator(cls, values):
        flag = values.get("bin_interpolation")
        groups = values.get("groups")
        has_function_params = any([att.function_uri.function_params is not None for att in groups])
        if flag is None and has_function_params:
            values["bin_interpolation"] = True
        elif flag is True and not has_function_params:
            raise ValueError("bin_interpolation flag applys to binning attributes only")
        return values


Query = Union[GroupByQuery, AggregationQuery, SelectQuery]
