from datetime import datetime
from api.model.Condition import Condition, CalculationOperator, ConditionGroup, LogicalOperator
from factdatasource.execptions import FDExecuteException
from munch import Munch


class SqlableDeleteCondition(object):
    """
    能生成删除语句的
    """

    def delete_condition_sql(self, table: str, condition_groups: list) -> str:
        return self.__condition_sql(table, condition_groups, "DELETE")

    def search_condition_sql(self, table: str, condition_groups: list) -> str:
        return self.__condition_sql(table, condition_groups, "SEARCH")

    def __condition_sql(self, table: str, condition_groups: list, method: str) -> str:
        """
        生成条件语句
        这里尽量用的是标准的SQL语法,如果有数据库不一样,就需要重载
        :param table:
        :param condition_groups:
        :param method:
        :return:
        """
        if method == "DELETE":
            sql = f"DELETE FROM `{table}` "
        else:
            sql = f"SELECT * FROM `{table}` "
        if condition_groups is None or len(condition_groups) == 0:
            return sql

        # 说明有查询条件组
        sql = sql + "WHERE "

        for index, condition_group in enumerate(condition_groups):
            if isinstance(condition_group, ConditionGroup):
                if index != 0:
                    sql = sql + f" {str(condition_group.operator.value)} "

                sql = sql + "("
                # 内部条件
                if condition_group.conditions is None or len(condition_group.conditions) == 0:
                    sql = sql + "1=1"
                else:
                    for jndex, condition in enumerate(condition_group.conditions):
                        if jndex != 0:
                            sql = sql + f" {condition.logical_operator.value} "
                        # 加入条件
                        sql = sql + f"`{condition.key}` {condition.calculation_operator.value} "
                        # 加入值
                        sql = sql + self.__generate_simple_value(condition.value)

                sql = sql + ")"
            else:
                if not isinstance(condition_group, dict):
                    raise FDExecuteException("查询条件格式错误")
                else:
                    try:
                        if index != 0:
                            operator = LogicalOperator(condition_group['operator'])
                            sql = sql + f" {str(operator.value)} "

                        sql = sql + "("
                        # 内部条件
                        if condition_group['conditions'] is None or len(condition_group['conditions']) == 0:
                            sql = sql + "1=1"
                        else:
                            for jndex, condition in enumerate(condition_group['conditions']):
                                if jndex != 0:
                                    if LogicalOperator.OR.name == condition['logicalOperator']:
                                        sql = sql + f" {LogicalOperator.OR.value} "
                                    else:
                                        sql = sql + f" {LogicalOperator.AND.value} "
                                # 加入条件
                                if CalculationOperator.EQUAL.name == condition['calculationOperator']:
                                    sql = sql + f"`{condition['key']}` {CalculationOperator.EQUAL.value} "
                                elif CalculationOperator.NOTEQUAL.name == condition['calculationOperator']:
                                    sql = sql + f"`{condition['key']}` {CalculationOperator.NOTEQUAL.value} "
                                elif CalculationOperator.GT.name == condition['calculationOperator']:
                                    sql = sql + f"`{condition['key']}` {CalculationOperator.GT.value} "
                                elif CalculationOperator.GTE.name == condition['calculationOperator']:
                                    sql = sql + f"`{condition['key']}` {CalculationOperator.GTE.value} "
                                elif CalculationOperator.LT.name == condition['calculationOperator']:
                                    sql = sql + f"`{condition['key']}` {CalculationOperator.LT.value} "
                                elif CalculationOperator.LTE.name == condition['calculationOperator']:
                                    sql = sql + f"`{condition['key']}` {CalculationOperator.LTE.value} "
                                elif CalculationOperator.IN.name == condition['calculationOperator']:
                                    sql = sql + f"`{condition['key']}` {CalculationOperator.IN.value} "
                                elif CalculationOperator.LIKE.name == condition['calculationOperator']:
                                    sql = sql + f"`{condition['key']}` {CalculationOperator.LIKE.value} "

                                # 加入值
                                sql = sql + self.__generate_simple_value(condition['value'])

                        sql = sql + ")"
                    except Exception:
                        raise FDExecuteException("查询条件格式错误")
        return sql

    def __generate_simple_value(self, value) -> str:
        """
        构造值的条件
        :param value:
        :return:
        """
        sql = ""

        if value is None:
            sql = "null"
        elif isinstance(value, str):
            sql = sql + f'"{value}"'
        elif isinstance(value, datetime):
            sql = sql + f'"{value.strftime("%Y-%m-%d %H:%M:%S")}"'
        elif isinstance(value, list) or isinstance(value, set):
            sql = sql + "("
            for index, obj in enumerate(value):
                sql = sql + self.__generate_simple_value(obj)
                if index != len(value) - 1:
                    sql = sql + ","
            sql = sql + ")"
        else:
            # 忽略是Map的情况
            sql = sql + f"{value}"
        return sql
