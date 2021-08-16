# -*- coding: utf-8 -*-
# @Time : 2020-05-08 15:48
# @Author : xzr
# @File : filters.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc :
import re
import warnings

import coreapi
import coreschema
import timezone_field
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend, filterset, filters
from rest_framework.filters import OrderingFilter as _OrderingFilter
from rest_framework.request import Request

from .response import RspError
from .serializer import s
from .utils.myenum import Enum
from .models import BaseModel

class OrderingFilter(_OrderingFilter):
    ordering_description = _('排序字段 -xxx 为倒序 如:-id')


class FilterQ(object):
    lookup_expr = 'exact'
    EMPTY_VALUES = ([], (), {}, '', None)

    DELIMITER = '__'

    def __init__(self, lookup_expr='', negated=False, connector=Q.AND):
        self.lookup_expr = lookup_expr or self.__class__.lookup_expr
        self.negated = negated
        self.connector = connector

    def get_q(self, field_name, values, connector=None):
        if values[0] in self.EMPTY_VALUES:
            return

        values = self.compose_values(values)
        if values is None:
            return
        lookup = self.get_lookup(field_name)
        q = Q(**{lookup: values})
        q.negated = self.negated
        q.connector = connector or self.connector
        return q

    def get_lookup(self, field_name):
        return '%s%s%s' % (field_name, self.DELIMITER, self.lookup_expr)

    def compose_values(self, values):
        return values[0]


class EmptyFilterQ(FilterQ):
    def compose_values(self, values):
        return ''


class RangeFilterQ(FilterQ):
    lookup_expr = 'range'
    EMPTY_VALUES = ('', ',', '-', '~')

    def compose_values(self, values):
        values = [v.strip() for v in re.split(' - |,|~', values[0])][:2]
        return values

    def get_q(self, field_name, values, connector=Q.AND):
        if values[0] in self.EMPTY_VALUES:
            return
        values = self.compose_values(values)
        min, max = values
        lookup_expr = self.lookup_expr
        if not min:
            values = max
            lookup_expr = 'lte'
        if not max:
            values = min
            lookup_expr = 'gte'

        lookup = '%s%s%s' % (field_name, self.DELIMITER, lookup_expr)
        q = Q(**{lookup: values})
        q.negated = self.negated
        q.connector = connector
        return q


class DateTimeRangeFilterQ(RangeFilterQ): pass


class InFilterQ(FilterQ):
    lookup_expr = 'in'

    def compose_values(self, values):
        return values


class BooleanFilterQ(FilterQ):
    def compose_values(self, values):
        if values[0] in (False, 'False', 'false', '0'):
            return False
        return True

class OperatorEnum(Enum):
    @classmethod
    def get_filter_q_obj(cls, operator_type):
        return cls(operator_type).other


class EqualOperator(OperatorEnum):
    Equal = 'exact', _('等于'), FilterQ()
    NotEqual = 'not_exact', _('不等于'), FilterQ(negated=True)


class NullOperator(OperatorEnum):
    NotNull = 'not_null', _('有值'), BooleanFilterQ(lookup_expr='isnull', negated=True)
    IsNull = 'is_null', _('没值'), BooleanFilterQ(lookup_expr='isnull', )


class InOperator(OperatorEnum):
    SingleIn = 'single_in', _('单选'), InFilterQ()
    In = 'in', _('多选'), InFilterQ()
    NotIn = 'not_in', _('反选'), InFilterQ(negated=True)


class CharOperator(EqualOperator, InOperator):
    """
    ## 字符串类型属性筛选

    判断类型	类比 SQL	描述说明
    等于	=	精确判断，只有选择的事件属性等于输入的判断值时，该事件才会才会进入分析过程；当判断值存在多个时，事件属性值等于任意一个，该事件都会进入分析的数据集
    不等于	!=	精确判断，只有选择的事件属性不等于输入的判断值时，该事件才会才会进入分析过程；当判断值存在多个时，事件属性值等于任意一个，该事件就不会进入分析过程
    包含	LIKE "%$判断值%"	匹配判断，当属性字段中包含判断值，该事件或用户就会进入分析过程
    不包含	NOT LIKE "%$判断值%"	匹配判断，与“包含”相反，当属性字段中包含判断值，该事件不会进入分析过程
    不为空	Length($属性)>0	当属性字段中有值(字符串长度大于 0 )时，事件或用户才会进入分析过程
    为空	=""	当属性字段中值为空字符串时，事件或用户才会进入分析过程
    没值	IS NULL	只有属性字段中值为 NULL 时，事件或用户才会进入分析过程
    有值	IS NOT NULL	只有属性字段中值不为 NULL 时，事件或用户才会进入分析过程
    正则匹配	匹配判断，符合条件的数据进入分析过程，具体请参考：正则表达式
    正则不匹配 匹配判断，只有不符合正则条件的数据进入分析过程，具体请参考：正则表达式
    """
    Contain = 'contains', _('包含'), FilterQ(lookup_expr='contains')
    NotContain = 'not_contains', _('不包含'), FilterQ(lookup_expr='contains', negated=True)
    IsEmpty = 'is_empty', _('为空'), EmptyFilterQ()
    NotEmpty = 'not_empty', _('不为空'), EmptyFilterQ(negated=True)
    # Rlike = 'rlike', _('正则匹配	匹配判断')
    # NotRlike = 'not_rlike', _('正则不匹配 匹配判断')


class NumberOperator(EqualOperator, InOperator):
    """
    ## 数值类型属性筛选

    判断类型	类比表达式	描述说明
    等于	=	类同于字符串类型
    不等于	!=	类同于字符串类型
    小于	<	所选属性值小于判断值的事件才会进入分析过程
    大于	>	所选属性值大于判断值的事件才会进入分析过程
    区间	between . and .	所选属性值处于设置的判断值所形成的闭区间时，事件才会进入分析流程；如判断值设置为 10 和 100 时，所选属性值需要满足 [10,100] 区间
    有值	IS NOT NULL	类同于字符串类型
    没值	IS NULL	类同于字符串类型
    时间类型属性筛选
    """
    GreaterThan = 'gt', _('大于'), FilterQ(lookup_expr='gt')
    LessThan = 'lt', _('小于'), FilterQ(lookup_expr='lt')
    Between = 'range', _('区间'), RangeFilterQ()


class DateTimeOperator(OperatorEnum):
    """
    ## 时间类型属性筛选

    绝对时间：有明确开始和截止时间的一个固定时间范围
    """
    Between = 'between', _('时间范围'), DateTimeRangeFilterQ()
    NotNull = 'not_null', _('有值'), BooleanFilterQ(lookup_expr='isnull', negated=True)
    IsNull = 'is_null', _('没值'), BooleanFilterQ(lookup_expr='isnull', )


class BoolOperator(NullOperator):
    """
    ## 布尔类型属性筛选
    """
    IsTrue = 'is_true', _('为真'), BooleanFilterQ()
    IsFalse = 'is_false', _('为假'), BooleanFilterQ()


class ChoiceOperator(InOperator, NullOperator): pass


class RelationEnum(Enum):
    And = 'and', _('与')
    Or = 'or', _('或')


class ConditionTypeEnum(Enum):
    Char = 'char', _('字符类'), CharOperator
    Number = 'number', _('数值类'), NumberOperator
    Bool = 'bool', _('布尔'), BoolOperator
    DateTime = 'date', _('日期时间'), DateTimeOperator
    Choice = 'choice', _('多选'), ChoiceOperator


    @classmethod
    def get_operator_type(cls, condition_type):
        return cls(condition_type).other

    @classmethod
    def get_schema(cls):
        schema_map = {}
        for k, v in cls.member_list():
            schema_map[k] = k.other.member_list()
        return schema_map


class MyFilterSerializer(s.Serializer):
    pass



class MyFilterBackend(DjangoFilterBackend):
    """
    # 准确等值
    name__exact = xx
    name__is_true = true
    """

    DELIMITER = FilterQ.DELIMITER

    @staticmethod
    def guess_condition_filter_q_obj(operator) -> FilterQ:

        for condition_type, _ in ConditionTypeEnum.member_list():
            operator_enum = ConditionTypeEnum.get_operator_type(condition_type)
            operator_type = operator_enum(operator)
            if operator_type:
                return operator_enum.get_filter_q_obj(operator)
        return None

    def get_filter_q(self, request, filterset_fields):
        condition_q = Q()
        relation = request.query_params.get('relation', )
        for key in request.query_params.keys():
            key_array = key.split(self.DELIMITER)
            if len(key_array) >= 2:
                name, operator = key_array[:2]
                if name not in filterset_fields:
                    raise RspError(_('%s 未被允许的筛选字段' % name))
                filter_q_obj: FilterQ = self.guess_condition_filter_q_obj(operator)
                if filter_q_obj is None:
                    raise RspError(_('%s 未定义操作类型' % operator))

                value_list = request.query_params.getlist(key)

                q = filter_q_obj.get_q(name, value_list)
                if q:
                    conn_type = RelationEnum(relation) or RelationEnum.And
                    condition_q.add(q, conn_type)
        return condition_q

    def filter_queryset(self, request: Request, queryset, view):
        filterset_fields = getattr(view, 'filter_fields', None)
        condition_q = self.get_filter_q(request, filterset_fields)
        queryset = queryset.filter(condition_q)
        return queryset

    @staticmethod
    def get_operator_enum(model_field):
        if isinstance(model_field, (models.ForeignKey, models.ManyToManyField, models.OneToOneField)) or getattr(
                model_field, 'choices', None):
            operator_enum = ConditionTypeEnum.Choice
        elif isinstance(model_field, (
                models.IntegerField, models.BigIntegerField, models.DecimalField, models.BigAutoField,
                models.AutoField)):
            operator_enum = ConditionTypeEnum.Number
        elif isinstance(model_field, (models.DateField, models.DateTimeField)):
            operator_enum = ConditionTypeEnum.DateTime
        elif isinstance(model_field, (models.BooleanField,)):
            operator_enum = ConditionTypeEnum.Bool
        else:
            operator_enum = ConditionTypeEnum.Char
        return operator_enum

    def generate_coreschema_from_model_field(self, field_name, model_field):
        from .schema import compose_enum_description
        field_cls = coreschema.String

        operator_enum = self.get_operator_enum(model_field)

        label = model_field.verbose_name or field_name

        field_enum_list = []

        for operator, _ in operator_enum.other.member_list():
            field_enum_list.append(('%s%s%s' % (operator, MyFilterBackend.DELIMITER, operator), operator.name))

        enum_description = compose_enum_description(field_enum_list)

        core_api_field = coreapi.Field(
                name=field_name,
                required=False,
                location='query',
                schema=field_cls(
                        description='%s\n%s' % (model_field.help_text or label, enum_description)
                )
        )
        return core_api_field

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'

        try:
            queryset = view.get_queryset()
        except Exception:
            queryset = view.model.objects.filter(id=-1)
            warnings.warn(
                    "%s is not compatible with schema generation" % view.__class__
            )

        filterset_class = self.get_filterset_class(view, queryset)
        model_class = filterset_class.Meta.model

        schema_fields = []
        if filterset_class:
            if issubclass(model_class,BaseModel):
                model_fields_map = model_class.get_fields_map()

                for field_name, field in filterset_class.base_filters.items():
                    model_field = model_fields_map.get(field_name, models.CharField())
                    schema_fields.append(self.generate_coreschema_from_model_field(field_name, model_field))
                schema_fields.append(coreapi.Field(
                        name='fields',
                        required=False,
                        location='query',
                        schema=coreschema.String(
                                description='需要返回的字段","号隔开:入 fields=id,name,alias,status'
                        )
                ))
                return schema_fields
        return []


filterset.FILTER_FOR_DBFIELD_DEFAULTS[timezone_field.TimeZoneField] = {'filter_class': filters.CharFilter}
