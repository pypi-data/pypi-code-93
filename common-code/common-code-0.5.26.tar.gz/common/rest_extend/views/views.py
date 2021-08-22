import abc
import datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Count
from django.db.models.query import QuerySet
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from copy import deepcopy
from common.rest_extend.response import (
    Results,
    SUCCESS,
    FAILURE,
    REQUEST_ERROR_CODE,
    SERVER_ERROR_CODE,
    PageTypeResults,
    get_error_status_code,
    RESTResponse,
)
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
                        orm_q.add(Q(**{real_key + "__" + keyword: values}), Q.AND)
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
        field, sort = self.get_sort(data, default_field="id", default_sort=self.DESC)
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

    def get(
            self,
            request,
            obj,
            obj_serializer,
            *,
            data=None,
            extend_conditions: dict = None,
            need_results=False,
            need_queryset=False,
            keys=None,
            **kwargs
    ):
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
        if not data:
            data = request.GET
        if extend_conditions:
            data = {**data, **extend_conditions}

        results, queryset, current_page_queryset = self.find(obj, data, obj_serializer)
        if need_results:
            return results
        if need_queryset:
            return results, queryset
        return RESTResponse(results)

    def post(self, request, obj, obj_serializer, *, data=None, need_results=False, **kwargs):
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
        if data.get("data"):
            data = data.get("data")
        serializer = obj_serializer(data=data)
        try:
            valid = serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            results.code, results.describe = get_error_status_code(e)
        else:
            results.describe = "add  successfully！！！"
            results.status = SUCCESS
            results.code = 200
        if need_results:
            return results
        return RESTResponse(results)

    def put(
            self,
            request,
            obj,
            obj_serializer,
            *,
            data=None,
            pk="id",
            extend_conditions: dict = None,
            need_results=False,
            need_queryset=False,
            **kwargs,
    ):
        instance = None
        results = Results()
        results.code = 200
        partial = True
        try:
            data, pk, value_pk, conditions = self.parsing_args_and_data(request, results, data, extend_conditions, pk)
            if results.code != 200:
                if need_results:
                    return results
                return RESTResponse(results)
            orm_q = self.get_orm_q(conditions)
            instance = obj.objects.filter(orm_q).first()
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
        if need_queryset:
            return results, instance
        return RESTResponse(results)

    def delete(
            self,
            request,
            obj,
            obj_serializer,
            *,
            data=None,
            pk="id",
            extend_conditions: dict = None,
            need_results=False,
            need_queryset=False,
            **kwargs,
    ):
        instance = None
        results = Results()
        results.code = 200
        try:
            data, pk, value_pk, conditions = self.parsing_args_and_data(request, results, data, extend_conditions, pk)
            if results.code != 200:
                if need_results:
                    return results
                return RESTResponse(results)
            orm_q = self.get_orm_q(conditions)
            instance = obj.objects.filter(orm_q).first()
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
        if need_queryset:
            return results, instance
        return RESTResponse(results)

    def get_queryset(self, obj, data) -> (QuerySet, QuerySet):
        return super(BaseView, self).get_queryset(obj, data)

    def parsing_args_and_data(self, request, results, data, extend_conditions, pk):
        conditions = {}
        if not extend_conditions:
            extend_conditions = {}
        if not data:
            data = request.data
        if data.get("data"):
            data = data.get("data")
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
                conditions = dict(**{pk: value_pk}, **extend_conditions)
            except Exception as e:
                results.code, results.describe = get_error_status_code(e)
        return data, pk, value_pk, conditions
