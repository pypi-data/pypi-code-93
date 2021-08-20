import abc
import datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Count
from django.db.models.query import QuerySet
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from copy import deepcopy

from common.rest_extend.decorator import relevance_vaild_legal_decorator
from common.rest_extend.response import (
    Results,
    SUCCESS,
    FAILURE,
    REQUEST_ERROR_CODE,
    SERVER_ERROR_CODE,
    PageTypeResults,
    get_error_status_code, RESTResponse,
)
from dataclasses import asdict, is_dataclass

# from django.core.paginator import Paginator, Page
from common.utility.args_parsing import BaseArgsParsing


class ResponseJsonEncoder(DjangoJSONEncoder):
    def default(self, o):
        _o = super(ResponseJsonEncoder, self).default(o)
        if isinstance(o, datetime.datetime):

            return o.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return _o


class Select(BaseArgsParsing, metaclass=abc.ABCMeta):
    GROUP = "group"

    RESERVED_FIELD = deepcopy(BaseArgsParsing.RESERVED_FIELD) + [GROUP]
    FORBID_VALUES = {GROUP: ["password"]}

    def get_orm_q(self, data):
        """
        获取筛选条件
        :param data:
        :return:
        """
        orm_q = Q()
        for key in data:
            if (not key) or (not data.get(key)):
                continue
            values = data.get(key)
            if key in self.FORBID_VALUES.keys():
                if any(item in values for item in self.FORBID_VALUES[key]):
                    raise ValueError(f" {key}  value cannot be a {values}")

            # 判断预留字段不当查询条件
            if key in self.RESERVED_FIELD:
                continue
            itme = key.split("_")
            if len(itme) > 1:
                real_key = "_".join(itme[:-1])
                keyword = itme[-1].lower()
                if keyword in self.SUFFIX_KEYWORD:
                    if keyword == self.LIKE:
                        orm_q.add(Q(**{real_key + "__contains": data.get(key)}), Q.AND)
                    elif keyword == self.IN:
                        values = data.get(key).split(",")
                        orm_q.add(Q(**{real_key + "__in": values}), Q.AND)
                    elif keyword == self.NOT:
                        orm_q.add(~Q(**{real_key: data.get(key)}), Q.AND)
                    else:
                        orm_q.add(Q(**{real_key + '__' + keyword: values}), Q.AND)
                    continue

            orm_q.add(Q(**{key: data.get(key)}), Q.AND)

        return orm_q

    def get_page_type_results(self, result, total, page, size, *args, **kwargs):
        """
        获取当前页面结果集
        :param result:
        :param total:
        :param page:
        :param size:
        :param args:
        :param kwargs:
        :return:
        """
        page_type_results = PageTypeResults()
        # page_type_results.group = group_result
        page_type_results.result = result
        page_type_results.total = total
        page_type_results.page = page
        page_type_results.size = size
        return page_type_results

    def paging(self, queryset, data, obj_serializer=None):
        """
        分页
        :param queryset:
        :param data:
        :return:
        """
        total = len(queryset)
        page, size = self.get_page_and_size(data)
        start = (page - 1) * size
        end = page * size
        current_page_queryset = queryset[start:end]
        current_page_result = []
        if current_page_queryset:
            # 如果是group  queryset是dict类型
            if not isinstance(current_page_queryset[0], dict):
                if obj_serializer:
                    current_page_result = list(obj_serializer(current_page_queryset, many=True).data)
                else:
                    current_page_result = list(queryset.values()[start:end])
            else:
                current_page_result = current_page_queryset
        return current_page_queryset, current_page_result, total, page, size

    def select(self, obj, data):
        """
        执行查询
        :param obj:
        :param data:
        :return:
        """
        orm_q = self.get_orm_q(data)
        queryset = obj.objects.select_related().filter(orm_q).all()
        return queryset

    def sort_queryset(self, data, queryset):
        """
        排序
        :param data:
        :param queryset:
        :return:
        """
        field, sort = self.get_sort(data, default_field='id', default_sort=self.DESC)
        queryset = queryset.order_by(field if Select.ASC == sort else f"-{field}")

        return queryset

    def group(self, obj, data):
        """
        group
        :param obj:
        :param data:
        :return:
        """
        orm_q = self.get_orm_q(data)
        group = data.get(self.GROUP)
        if group:
            group = tuple(group.split(","))
            queryset = obj.objects.select_related().filter(orm_q).all()
            queryset = queryset.values(*group).annotate(count=Count("id"))
        else:
            raise Exception(f"'{self.GROUP}'  is None!!!")
        return queryset

    def find(self, obj, data, obj_serializer=None):
        """
        查询、并返回Results
        1、获取queryset
        2、排序
        3、分页
        4、获取当前页结果
        5、扩展当前页结果
        :param obj:
        :param data:
        :return:
        """
        results = Results()
        queryset = None
        current_page_queryset = None
        try:
            # 获取queryset ；extend_queryset用于扩展页面数据集
            queryset, extend_queryset = self.get_queryset(obj, data)
            queryset = self.sort_queryset(data, queryset)
            current_page_queryset, current_page_result, total, page, size = self.paging(queryset, data, obj_serializer)
            page_type_results = self.get_page_type_results(current_page_result, total, page, size)
            self.extend_page_type_results(data, page_type_results, extend_queryset)
            results.data = page_type_results
            results.data_length = len(page_type_results.result)
            results.code = 200
        except Exception as e:
            results.code, results.describe = get_error_status_code(e)
        return results, queryset, current_page_queryset

    @abc.abstractmethod
    def get_queryset(self, obj, data) -> (QuerySet, QuerySet):
        group = data.get(self.GROUP)
        if group:
            queryset = self.group(obj, data)
        else:
            queryset = self.select(obj, data)
        return queryset, None

    def extend_page_type_results(self, data, page_type_results, extend_queryset, *args, **kwargs):
        pass


class BaseView(APIView, Select):
    """
    对实体模型增删改查的父类
    """

    def get(self, request, obj, obj_serializer, data=None, need_results=False, need_queryset=False, keys=None):
        """
        根据键值对查找数据
        :param request:
        :param obj:
        :param obj_serializer:
        :param data:
        :param need_results:
        :param keys:
        :return:
        """
        results, queryset, current_page_queryset = self.find(obj, request.GET, obj_serializer)
        if need_results:
            return results
        if need_queryset:
            return results, queryset
        return RESTResponse(results)

    def post(self, request, obj, obj_serializer, data=None, need_results=False, **kwargs):
        """
        添加数据
        :param request:
        :param obj:
        :param obj_serializer:
        :param data:
        :param need_results:
        :return:
        """
        results = Results()
        if not data:
            data = request.data
        if data.get('data'):
            data = data.get('data')
        serializer = obj_serializer(data=data)
        try:
            valid = serializer.is_valid(raise_exception=True)
            serializer.save()
            results.describe = "add  successfully！！！"
            results.status = SUCCESS
            results.code = 200
        except Exception as e:
            results.code, results.describe = get_error_status_code(e)

        if need_results:
            return results
        return RESTResponse(results)

    def put(self, request, obj, obj_serializer, data=None, need_results=False, pk="id", **kwargs):
        """
        根据主键，或某个字段更新数据
        :param request:
        :param obj:
        :param obj_serializer:
        :param data:
        :param need_results:
        :param pk:
        :return:
        """
        results = Results()
        results.code = 200
        if not data:
            data = request.data
        if data.get('data'):
            data = data.get('data')
        partial = True
        if request.GET.get("pk"):
            pk = request.GET.get("pk")
        try:
            value_pk = data.get(pk)
            if not value_pk:
                results.describe = "'pk' cannot be empty"
                results.code = REQUEST_ERROR_CODE

            else:
                if pk == "id":
                    try:
                        value_pk = int(value_pk)
                    except:
                        raise ValidationError("'pk' type error Should be <int>！！！")

                instance = obj.objects.filter(**{pk: value_pk}).first()
                if not instance:
                    results.describe = pk + "=" + str(value_pk) + "  does not exist"
                    results.code = REQUEST_ERROR_CODE
                else:

                    serializer = obj_serializer(instance, data=data, partial=partial)
                    try:
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        results.describe = "update  successfully！！！"
                        results.status = SUCCESS
                    except Exception as e:
                        results.code, results.describe = get_error_status_code(e)
                    if getattr(instance, "_prefetched_objects_cache", None):
                        # If 'prefetch_related' has been applied to a queryset, we need to
                        # forcibly invalidate the prefetch cache on the instance.
                        instance._prefetched_objects_cache = {}

        except Exception as e:
            results.code, results.describe = get_error_status_code(e)

        if need_results:
            return results
        return RESTResponse(results)

    def delete(self, request, obj, obj_serializer, data=None, need_results=False, pk="id", **kwargs):
        """
        根据主键删除数据
        :param request:
        :param obj:
        :param obj_serializer:
        :param data:
        :param need_results:
        :param pk:
        :return:
        """
        results = Results()
        results.code = 200
        if not data:
            data = request.data
        if data.get('data'):
            data = data.get('data')
        if request.GET.get("pk"):
            pk = request.GET.get("pk")
        value_pk = data.get(pk)
        if not value_pk:
            results.describe = "'pk' cannot be empty"
            results.code = REQUEST_ERROR_CODE
        else:
            try:
                if pk == "id":
                    try:
                        value_pk = int(value_pk)
                    except:
                        raise ValidationError("'pk' type error Should be <int>！！！")

                instance = obj.objects.filter(id=value_pk).first()
                if not instance:
                    results.describe = pk + "=" + str(value_pk) + " does not exist"
                    results.code = REQUEST_ERROR_CODE
                else:
                    instance.delete()
                    results.describe = "deleted successfully！！！"
                    results.status = SUCCESS
            except Exception as e:
                results.code, results.describe = get_error_status_code(e)

        if need_results:
            return results
        return RESTResponse(results)

    def get_queryset(self, obj, data) -> (QuerySet, QuerySet):
        return super(BaseView, self).get_queryset(obj, data)


class BaseJoinView(APIView, Select):
    CHOOSE_GROUP = "choosegroup"
    RESERVED_FIELD = deepcopy(Select.RESERVED_FIELD) + [CHOOSE_GROUP]
    FORBID_VALUES = dict(**Select.FORBID_VALUES, **{CHOOSE_GROUP: ["password"]})

    @relevance_vaild_legal_decorator
    def get(self, request, obj, obj_serializer, obj_relevance=None, m_to_m_obj=None, mapping: dict = None,
            m_to_m_mapping=None):
        """
        扩展返回字段（关联表）
        1、获取queryset
        2、扩展字段
        :param request:
        :param obj:
        :param obj_serializer:
        :param obj_relevance: 外键关联对象
        :param mapping: 需要扩展字段对应的映射
        :return:
        """
        results, queryset, current_page_queryset = self.find(obj, request.GET, obj_serializer)
        if results.data and results.data.result and mapping and obj_relevance:
            result = self.extend_result_field(obj_serializer, obj_relevance, m_to_m_obj, mapping, m_to_m_mapping,
                                              current_page_queryset)
            results.data.result = result
        return RESTResponse(results)

    def post(self, request, obj, obj_serializer, obj_relevance: list = None, m_to_m_obj: list = None,
             mapping=None,
             m_to_m_mapping=None, data=None):
        results = Results()
        if not data:
            data = request.data
        if data.get('data'):
            data = data.get('data')
        serializer = obj_serializer(data=data)
        if obj_relevance and mapping:
            for obj in obj_relevance:
                obj_name = obj.__name__.lower()
                obj_mapping = mapping.get(obj_name)
                if not obj_mapping:
                    raise Exception(f'{obj_name}  are not mapping!!!')
                queryset = self.get_relevance_queryset(obj, obj_name, data)
                self.extend_relevance_data(data, queryset, obj_mapping)
        if m_to_m_obj and m_to_m_mapping:
            for obj in m_to_m_obj:
                pass
        try:
            valid = serializer.is_valid(raise_exception=True)
            serializer.save()
            results.describe = "add  successfully！！！"
            results.status = SUCCESS
            results.code = 200
        except Exception as e:
            results.code, results.describe = get_error_status_code(e)

        return RESTResponse(results)

    def delete(self, request, obj, obj_serializer, data=None, pk="id", **kwargs):
        """
        根据主键删除数据
        :param request:
        :param obj:
        :param obj_serializer:
        :param data:
        :param need_results:
        :param pk:
        :return:
        """
        results = Results()
        results.code = 200
        if not data:
            data = request.data
        if data.get('data'):
            data = data.get('data')
        if request.GET.get("pk"):
            pk = request.GET.get("pk")
        value_pk = data.get(pk)
        if not value_pk:
            results.describe = "'pk' cannot be empty"
            results.code = REQUEST_ERROR_CODE
        else:
            try:
                if pk == "id":
                    try:
                        value_pk = int(value_pk)
                    except:
                        raise ValidationError("'pk' type error Should be <int>！！！")

                instance = obj.objects.filter(id=value_pk).first()
                if not instance:
                    results.describe = pk + "=" + str(value_pk) + " does not exist"
                    results.code = REQUEST_ERROR_CODE
                else:
                    instance.delete()
                    results.describe = "deleted successfully！！！"
                    results.status = SUCCESS
            except Exception as e:
                results.code, results.describe = get_error_status_code(e)

        return RESTResponse(results)

    def extend_relevance_data(self, data, queryset, obj_mapping):
        if queryset:
            value = getattr(queryset, obj_mapping[0], None)
            if value is not None:
                data[obj_mapping[1]] = value

    def get_relevance_orm_q(self, obj_name, data):
        conditions = {}
        for item, value in data.items():
            if obj_name + '__' in item:
                conditions[item.replace(obj_name + '__', '')] = value
        if conditions:
            orm_q = self.get_orm_q(conditions)
            return orm_q

    def get_relevance_queryset(self, obj, obj_name, data):
        orm_q = self.get_relevance_orm_q(obj_name, data)
        queryset = obj.objects.filter(orm_q).first()
        return queryset

    def extend_result_field(self, obj_serializer, obj_relevance, m_to_m_obj, mapping, m_to_m_mapping, queryset):
        """
        扩展字段
        1、获取关联表
        2、遍历结果集、进行字段扩展
        :param obj_relevance:
        :param mapping:
        :param queryset:
        :return:
        """

        result = []
        # 遍历结果集
        for item in queryset:
            item_result = item if isinstance(item, dict) else dict(obj_serializer(item).data)
            self.extend_m_to_m_field(item, item_result, m_to_m_obj, m_to_m_mapping)
            self.extend_relevance_field(item, item_result, obj_relevance, mapping)
            result.append(item_result)
        return result

    def extend_m_to_m_field(self, item, item_result, m_to_m_obj, m_to_m_mapping):
        if m_to_m_obj:
            m_to_m_name = m_to_m_obj.__name__.lower()
            item_result[m_to_m_name] = []
            m_to_m = getattr(item, m_to_m_name).all()
            for m_to_m_obj in m_to_m:
                for key in m_to_m_mapping:
                    value = getattr(m_to_m_obj, m_to_m_mapping[key])
                    if value:
                        item_result[key].append(value)

    def extend_relevance_field(self, item, item_result, obj_relevance, mapping):
        # 获取关联表
        relevance_name = obj_relevance.__name__.lower()
        # 获取queryset中的外键对象
        _obj = getattr(item, relevance_name)
        # 对结果集进行字段扩展
        for key in mapping:
            child_obj = _obj
            if child_obj:
                # 多级 关联
                if "." in mapping[key]:
                    attrs = mapping[key].split(".")
                    # 多级 关联的外键对象
                    child_obj = getattr(_obj, attrs[0])
                    for attr in attrs[1:]:
                        child_obj = getattr(child_obj, attr)
                    item_result[key] = child_obj
                else:
                    item_result[key] = getattr(_obj, mapping[key], None)
            else:
                item_result[key] = None

    def get_queryset(self, obj, data) -> (QuerySet, QuerySet):

        drop_group = data.get(self.CHOOSE_GROUP)
        queryset, extend_queryset = super().get_queryset(obj, data)
        if drop_group:
            group = tuple(drop_group.split(","))
            extend_queryset = queryset.values(*group).annotate(count=Count("id"))
        return queryset, extend_queryset

    # def get_page_type_results(self, result, total, page, size, group_result=None, **kwargs):
    #     if not group_result:
    #         group_result = {}
    #     page_type_results = super().get_page_type_results(result, total, page, size)
    #     page_type_results.group = group_result
    #     return page_type_results

    def extend_page_type_results(self, data, page_type_results, extend_queryset, *args, **kwargs):
        if extend_queryset:
            page_type_results.group = list(extend_queryset)
