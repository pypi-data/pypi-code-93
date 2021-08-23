from typing import Union

from pydantic import BaseModel

from igenius_adapters_sdk.entities.i18n import I18n

Uid = str

StaticTypes = Union[float, int, str]


class AttributeFunctionSpecs(BaseModel):
    uid: Uid
    i18n: I18n


class AggregationFunction:
    IDENTITY = AttributeFunctionSpecs(
        uid="crystal.topics.data.aggregation.identity",
        i18n=I18n(
            name="cons-conf-core-data-editor-aggregation-function-identity",
            description="crystal.topics.data.aggregation.identity.i18n.description",
        ),
    )

    AVG = AttributeFunctionSpecs(
        uid="crystal.topics.data.aggregation.avg",
        i18n=I18n(
            name="cons-configure-data-editor-agg-fun-average",
            description="crystal.topics.data.aggregation.avg.i18n.description",
        ),
    )

    COUNT = AttributeFunctionSpecs(
        uid="crystal.topics.data.aggregation.count",
        i18n=I18n(
            name="cons-configure-data-editor-agg-fun-count",
            description="crystal.topics.data.aggregation.count.i18n.description",
        ),
    )

    SUM = AttributeFunctionSpecs(
        uid="crystal.topics.data.aggregation.sum",
        i18n=I18n(
            name="cons-configure-data-editor-agg-fun-sum",
            description="crystal.topics.data.aggregation.sum.i18n.description",
        ),
    )

    DISTINCT_COUNT = AttributeFunctionSpecs(
        uid="crystal.topics.data.aggregation.distinct-count",
        i18n=I18n(
            name="cons-conf-core-data-editor-aggregation-function-distinct-count",
            description="crystal.topics.data.aggregation.distinct-count.i18n.description",
        ),
    )

    MIN = AttributeFunctionSpecs(
        uid="crystal.topics.data.aggregation.min",
        i18n=I18n(
            name="cons-configure-data-editor-agg-fun-min",
            description="crystal.topics.data.aggregation.min.i18n.description",
        ),
    )

    MAX = AttributeFunctionSpecs(
        uid="crystal.topics.data.aggregation.max",
        i18n=I18n(
            name="cons-configure-data-editor-agg-fun-max",
            description="crystal.topics.data.aggregation.max.i18n.description",
        ),
    )

    STATIC = AttributeFunctionSpecs(
        uid="crystal.topics.data.aggregation.static",
        i18n=I18n(
            name="cons-conf-core-data-editor-aggregation-function-distinct-static",
            description="crystal.topics.data.aggregation.static.i18n.description",
        ),
    )

    @classmethod
    def from_uid(cls, uid: str) -> AttributeFunctionSpecs:
        """Given an aggregation function uid, returns its complete spec if found,
        otherwise raises ValueError."""
        try:
            return next(
                value
                for attr, value in cls.__dict__.items()
                if isinstance(value, AttributeFunctionSpecs) and value.uid == uid.lower()
            )
        except StopIteration:
            raise ValueError(f"Invalid AggregationFunction uid={uid}")


class GroupByFunction:
    IDENTITY = AttributeFunctionSpecs(
        uid="crystal.topics.data.group-by.identity",
        i18n=I18n(
            name="cons-conf-core-data-editor-aggregation-function-identity",
            description="crystal.topics.data.group-by.identity.i18n.description",
        ),
    )

    DATE_TRUNC_DAY = AttributeFunctionSpecs(
        uid="crystal.topics.data.group-by.date-trunc-day",
        i18n=I18n(
            name="cons-conf-core-data-editor-aggregation-function-day",
            description="crystal.topics.data.group-by.date-trunc-day.i18n.description",
        ),
    )

    DATE_TRUNC_WEEK = AttributeFunctionSpecs(
        uid="crystal.topics.data.group-by.date-trunc-week",
        i18n=I18n(
            name="cons-conf-core-data-editor-aggregation-function-week",
            description="crystal.topics.data.group-by.date-trunc-week.i18n.description",
        ),
    )

    DATE_TRUNC_MONTH = AttributeFunctionSpecs(
        uid="crystal.topics.data.group-by.date-trunc-month",
        i18n=I18n(
            name="cons-conf-core-data-editor-aggregation-function-month",
            description="crystal.topics.data.group-by.date-trunc-month.i18n.description",
        ),
    )

    DATE_TRUNC_QUARTER = AttributeFunctionSpecs(
        uid="crystal.topics.data.group-by.date-trunc-quarter",
        i18n=I18n(
            name="cons-conf-core-data-editor-aggregation-function-quarter",
            description="crystal.topics.data.group-by.date-trunc-quarter.i18n.description",
        ),
    )

    DATE_TRUNC_SEMESTER = AttributeFunctionSpecs(
        uid="crystal.topics.data.group-by.date-trunc-semester",
        i18n=I18n(
            name="cons-conf-core-data-editor-aggregation-function-semester",
            description="crystal.topics.data.group-by.date-trunc-semester.i18n.description",
        ),
    )

    DATE_TRUNC_YEAR = AttributeFunctionSpecs(
        uid="crystal.topics.data.group-by.date-trunc-year",
        i18n=I18n(
            name="cons-conf-core-data-editor-aggregation-function-year",
            description="crystal.topics.data.group-by.date-trunc-year.i18n.description",
        ),
    )

    NUMERIC_BINNING = AttributeFunctionSpecs(
        uid="crystal.topics.data.group-by.numeric_binning",
        i18n=I18n(
            name="cons-conf-core-data-editor-aggregation-function-numeric-binning",
            description="crystal.topics.data.group-by.numeric_binning.i18n.description",
        ),
    )

    @classmethod
    def from_uid(cls, uid: str) -> AttributeFunctionSpecs:
        """Given a groupby function uid, returns its complete spec if found,
        otherwise raises ValueError."""
        try:
            return next(
                value
                for attr, value in cls.__dict__.items()
                if isinstance(value, AttributeFunctionSpecs) and value.uid == uid.lower()
            )
        except StopIteration:
            raise ValueError(f"Invalid GroupByFunction uid={uid}")
