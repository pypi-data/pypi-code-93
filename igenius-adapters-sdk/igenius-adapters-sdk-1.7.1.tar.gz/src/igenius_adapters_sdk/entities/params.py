from typing import Any, Mapping, NewType, Tuple, Type

from pydantic import BaseModel, Extra, Field

from igenius_adapters_sdk.entities.i18n import I18n

Uid = NewType("Uid", str)


class ParamOperationSpecs(BaseModel):
    uid: Uid = Field(..., description="uid of the operation")
    i18n: I18n
    properties_schema: Mapping[str, Any] = Field(
        ..., description="jsonschema of expected payload when using the operation"
    )


class OperationPropertiesSchema:
    class NoValue(BaseModel):
        class Config:
            extra = Extra.forbid

    class SingleValue(BaseModel):
        data: str

        class Config:
            extra = Extra.forbid

    class MultipleValue(BaseModel):
        data: Tuple[str, ...]

        class Config:
            extra = Extra.forbid

    class RangeValue(BaseModel):
        start: str
        end: str

        class Config:
            extra = Extra.forbid


class OperationSchemaSpec(BaseModel):
    model: Type[BaseModel]
    jsonschema: Mapping[str, Any]

    class Config:
        arbitrary_types_allowed = True


class OperationSchemas:
    NO_VALUE = OperationSchemaSpec(
        model=OperationPropertiesSchema.NoValue,
        jsonschema=OperationPropertiesSchema.NoValue.schema(),
    )
    SINGLE_VALUE = OperationSchemaSpec(
        model=OperationPropertiesSchema.SingleValue,
        jsonschema=OperationPropertiesSchema.SingleValue.schema(),
    )
    MULTIPLE_VALUE = OperationSchemaSpec(
        model=OperationPropertiesSchema.MultipleValue,
        jsonschema=OperationPropertiesSchema.MultipleValue.schema(),
    )
    RANGE_VALUE = OperationSchemaSpec(
        model=OperationPropertiesSchema.RangeValue,
        jsonschema=OperationPropertiesSchema.RangeValue.schema(),
    )

    @classmethod
    def from_jsonschema(cls, jsonschema: Mapping[str, Any]) -> OperationSchemaSpec:
        """Given the jsonschema, finds the entire OperationSchema that generated it,
        or raises ValueError if not found."""
        try:
            return next(
                value
                for attr, value in cls.__dict__.items()
                if isinstance(value, OperationSchemaSpec) and value.jsonschema == jsonschema
            )
        except StopIteration:
            raise ValueError("OperationSchema not found")


class ParamOperation:
    EQUAL = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.equal",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-equal",
            description="crystal.topics.data.param-operation.equal.i18n.description",
        ),
        properties_schema=OperationSchemas.SINGLE_VALUE.jsonschema,
    )
    DIFFERENT = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.different",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-different",
            description="crystal.topics.data.param-operation.different.i18n.description",
        ),
        properties_schema=OperationSchemas.SINGLE_VALUE.jsonschema,
    )
    GREATER_THAN = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.greater-than",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-greater-than",
            description="crystal.topics.data.param-operation.greater-than.i18n.description",
        ),
        properties_schema=OperationSchemas.SINGLE_VALUE.jsonschema,
    )
    LESS_THAN = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.less-than",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-less-than",
            description="crystal.topics.data.param-operation.less-than.i18n.description",
        ),
        properties_schema=OperationSchemas.SINGLE_VALUE.jsonschema,
    )
    GREATER_THAN_OR_EQUAL_TO = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.greater-than-or-equal-to",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-greater-than-equal-to",
            description="crystal.topics.data.param-operation.greater-than-or-equal-to.i18n.description",  # noqa: E501
        ),
        properties_schema=OperationSchemas.SINGLE_VALUE.jsonschema,
    )
    LESS_THAN_OR_EQUAL_TO = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.less-than-or-equal-to",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-less-than-equal-to",
            description="crystal.topics.data.param-operation.less-than-or-equal-to.i18n.description",
        ),
        properties_schema=OperationSchemas.SINGLE_VALUE.jsonschema,
    )
    BETWEEN = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.between",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-between",
            description="crystal.topics.data.param-operation.between.i18n.description",
        ),
        properties_schema=OperationSchemas.RANGE_VALUE.jsonschema,
    )
    CONTAINS = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.contains",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-contains",
            description="crystal.topics.data.param-operation.contains.i18n.description",
        ),
        properties_schema=OperationSchemas.SINGLE_VALUE.jsonschema,
    )
    IN = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.in",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-in",
            description="crystal.topics.data.param-operation.in.i18n.description",
        ),
        properties_schema=OperationSchemas.MULTIPLE_VALUE.jsonschema,
    )
    NOT_CONTAINS = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.not-contains",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-not-contains",
            description="crystal.topics.data.param-operation.not-contains.i18n.description",
        ),
        properties_schema=OperationSchemas.SINGLE_VALUE.jsonschema,
    )
    STARTS_WITH = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.starts-with",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-starts-with",
            description="crystal.topics.data.param-operation.starts-with.i18n.description",
        ),
        properties_schema=OperationSchemas.SINGLE_VALUE.jsonschema,
    )
    ENDS_WITH = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.ends-with",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-ends-with",
            description="crystal.topics.data.param-operation.ends-with.i18n.description",
        ),
        properties_schema=OperationSchemas.SINGLE_VALUE.jsonschema,
    )
    EMPTY = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.empty",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-empty",
            description="crystal.topics.data.param-operation.empty.i18n.description",
        ),
        properties_schema=OperationSchemas.NO_VALUE.jsonschema,
    )
    NOT_EMPTY = ParamOperationSpecs(
        uid="crystal.topics.data.param-operation.not-empty",
        i18n=I18n(
            name="cons-data-table-sort-operation-label-not-empty",
            description="crystal.topics.data.param-operation.not-empty.i18n.description",
        ),
        properties_schema=OperationSchemas.NO_VALUE.jsonschema,
    )

    @classmethod
    def from_uid(cls, uid: str) -> ParamOperationSpecs:
        """Given a param operation uid, returns its complete spec if found,
        otherwise raises ValueError."""
        try:
            return next(
                value
                for attr, value in cls.__dict__.items()
                if isinstance(value, ParamOperationSpecs) and value.uid == uid.lower()
            )
        except StopIteration:
            raise ValueError(f"Invalid ParamOperation uid={uid}")
