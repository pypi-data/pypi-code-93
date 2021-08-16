from enum import Enum


class LogicalOperator(Enum):
    OR = "OR"
    AND = "AND"


class CalculationOperator(Enum):
    EQUAL = "="
    NOTEQUAL = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    IN = "in"
    LIKE = "like"


class ConditionGroup:
    def __init__(self, operator: LogicalOperator, conditions: list):
        """

        :param operator:
        :param conditions:
        """
        self.conditions = conditions
        self.operator = operator


class Condition:

    def __init__(self, logical_operator: LogicalOperator, key: str, value, calculation_operator: CalculationOperator):
        """

        :param logical_operator:
        :param key:
        :param value:
        :param calculation_operator:
        """
        self.logical_operator: LogicalOperator = logical_operator
        self.key = key
        self.value = value
        self.calculation_operator: CalculationOperator = calculation_operator
