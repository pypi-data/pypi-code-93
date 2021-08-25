import json
import os
import re
from enum import Enum, auto
from typing import List, Optional, Union
from dataclasses import dataclass


class SQLFunction(Enum):
    MAX = auto()
    MIN = auto()
    AVG = auto()
    COUNT = auto()
    SUM = auto()


class TimeDimensionGranularity(Enum):
    year = auto()
    quarter = auto()
    month = auto()
    week = auto()
    day = auto()
    hour = auto()
    interval = auto()


class SignOperator(Enum):
    NEXT = auto()
    PREV = auto()


@dataclass
class Field:
    column: str
    aggregation: Optional[Union[SQLFunction, TimeDimensionGranularity, str]] = None
    dataset: Optional[str] = None
    entityType: Optional[str] = None
    alias: Optional[str] = None


class SQLOperator(Enum):
    EQ = auto()
    NOT_EQ = auto()
    GOE = auto()
    GT = auto()
    LOE = auto()
    LT = auto()
    IN = auto()
    NOT_IN = auto()
    FOREACH = auto()


class BooleanOperator(Enum):
    AND = auto()
    OR = auto()


class PeriodOperator(Enum):
    PREV = auto()
    CURR = auto()
    NEXT = auto()


class TimeOperator(Enum):
    RANGE = auto()
    FROM = auto()
    TO = auto()


@dataclass
class Condition:
    field: Field
    operator: Union[SQLOperator, TimeOperator, str]
    value: Optional[List[Union[float, str]]] = None
    type: Optional[str] = None
    steps: Optional[str] = None
    interval: Optional[str] = None
    direction: Optional[Union[PeriodOperator, str]] = None
    negate: Optional[bool] = None

    def __repr__(self):
        vars = []
        if self.value is not None:
            for var in self.value:
                vars.append(str(var))
            formatted_value = "( " + ", ".join(vars) + " )"
        else:
            formatted_value = None

        if isinstance(self.operator, str):
            operator = self.operator
        else:
            operator = self.operator.name
            if operator == "GOE":
                operator = ">="
            elif operator == "LOE":
                operator = "<="
            elif operator == "EQ":
                operator = "=="
            elif operator == "GT":
                operator = ">"
            elif operator == "LT":
                operator = "<"
        field_with_agg = self.field.column
        if self.field.aggregation is not None:
            if isinstance(self.field.aggregation, SQLFunction) or isinstance(self.field.aggregation,
                                                                                  TimeDimensionGranularity):
                field_with_agg = self.field.aggregation.name + " ( " + field_with_agg + " )"
            else:
                field_with_agg = self.field.aggregation + " ( " + field_with_agg + " )"
        else:
            field_with_agg = field_with_agg
        if formatted_value is not None and self.direction is None:
            where_condition = (
                    field_with_agg + " " + operator + " " + str(formatted_value)
            )
        elif formatted_value is None and self.direction is not None:
            if isinstance(self.direction, PeriodOperator):
                direction = self.direction.name
            else:
                direction = self.direction
            if self.steps is not None and self.interval is not None:
                where_condition = (
                    field_with_agg + " " + operator + " " + self.interval + " " + direction + " " + self.steps
                )
            elif self.steps is not None and self.interval is None:
                where_condition = (
                        field_with_agg + " " + operator + " " + direction + " " + self.steps
                )
            elif self.steps is None and self.interval is not None:
                where_condition = (
                        field_with_agg + " " + operator + " " + self.interval + " " + direction
                )
            else:
                where_condition = (
                        field_with_agg + " " + operator + " " + direction
                )
        else:
            where_condition = (
                    field_with_agg + " " + operator
            )

        return where_condition


@dataclass
class CompositeCondition:
    operator: BooleanOperator
    conditions: List[Union[Condition, 'CompositeCondition']]

    def __repr__(self):
        where_condition = '( ' + (' ' + self.operator.name + ' ').join([str(c) for c in self.conditions]) + ' )'

        return where_condition


class SQLSorting(Enum):
    DESC = auto()
    ASC = auto()


@dataclass
class Sorting:
    field: str
    order: SQLSorting


@dataclass
class Component:
    type: str
    queryId: str


@dataclass
class QueryComponent(Component):
    category: str


@dataclass
class ChartComponent(Component):
    chartType: str


@dataclass
class MapComponent(Component):
    mapType: str


@dataclass
class From:
    dataset: str


@dataclass
class Query:
    fields: List[Field]
    id: Optional[str] = None
    datasets: Optional[List[From]] = None
    where: Optional[List[Union[Condition, CompositeCondition]]] = None
    orderBy: Optional[List[Sorting]] = None
    limit: Optional[Union[int, str]] = None

    def to_sql(self, dataset: str = None):
        sql = "SELECT {} FROM {}"

        fields_with_agg = []
        for field in self.fields:
            column = field.column
            if field.aggregation is not None:
                if isinstance(field.aggregation, SQLFunction) or isinstance(field.aggregation, TimeDimensionGranularity):
                    field_with_agg = field.aggregation.name + " ( " + column + " )"
                else:
                    field_with_agg = field.aggregation + " ( " + column + " )"
            else:
                field_with_agg = column
            if field.alias is not None:
                field_with_agg += " AS " + field.alias
            fields_with_agg.append(field_with_agg)

        formatted_fields = ", ".join(fields_with_agg)

        froms_array = []
        if self.datasets is not None:
            for f in self.datasets:
                froms_array.append(f.dataset)
            table = ", ".join(froms_array)
        elif dataset is not None:
            table = dataset
        else:
            table = "{{dataset.A}}"
        sql = sql.format(formatted_fields, table)

        where_conditions = []
        if self.where is not None:
            sql_where = " WHERE {}"

            for condition in self.where:
                where_condition = str(condition)
                where_conditions.append(where_condition)
            if where_conditions:
                formatted_where_conditions = " AND ".join(where_conditions)
                sql_where = sql_where.format(formatted_where_conditions)
                sql += sql_where

        sorting_conditions = []
        if self.orderBy is not None:
            sql_orderby = " ORDER BY {}"

            for sorting in self.orderBy:
                sort_order = sorting.order.name
                sort_condition = sorting.field + " " + sort_order
                sorting_conditions.append(sort_condition)

            formatted_sorting = ", ".join(sorting_conditions)
            sql_orderby = sql_orderby.format(formatted_sorting)
            sql += sql_orderby

        if self.limit is not None:
            sql += " LIMIT " + str(self.limit)

        return sql


@dataclass
class SmartQuery:
    queries: List[Query]
    components: Optional[List[Union[ChartComponent, MapComponent, QueryComponent, Component]]] = None
    javascript: Optional[List[str]] = None

    @staticmethod
    def _get_tokens():
        f = open(os.path.join(os.path.dirname(__file__), "askdata_config", "compression_tokens.json"))
        comp_tokens = json.load(f)
        f.close()
        return comp_tokens

    @staticmethod
    def compress(smartquery_json: str):
        comp_tokens = SmartQuery._get_tokens()
        for token in comp_tokens:
            extended = token['decode']
            code = token['code']
            if extended in smartquery_json:
                smartquery_json = re.sub(r"\b"+extended+r"\b", code, smartquery_json)
        return smartquery_json

    @staticmethod
    def decompress(smartquery_json: str):
        comp_tokens = SmartQuery._get_tokens()
        for token in comp_tokens:
            code = token['code']
            decode = token['decode']
            if code in smartquery_json:
                smartquery_json = re.sub(r"\b"+code+r"\b", decode, smartquery_json)
        return smartquery_json
