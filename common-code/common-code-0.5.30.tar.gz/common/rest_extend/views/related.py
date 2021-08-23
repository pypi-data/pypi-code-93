from copy import deepcopy

from django.db.models import Count
from django.db.models.query import QuerySet
from rest_framework.exceptions import ValidationError
from common.rest_extend.response import RESTResponse, Results, SUCCESS, get_error_status_code, REQUEST_ERROR_CODE
from common.rest_extend.decorator import related_vaild_legal_decorator
from rest_framework.views import APIView
from common.rest_extend.views.views import Select, BaseView


class RelatedView(BaseView):
    CHOOSE_GROUP = "choosegroup"
    RESERVED_FIELD = deepcopy(Select.RESERVED_FIELD) + [CHOOSE_GROUP]
    FORBID_VALUES = dict(**Select.FORBID_VALUES, **{CHOOSE_GROUP: ["password"]})

    @related_vaild_legal_decorator
    def get(
            self,
            request,
            obj,
            obj_serializer,
            data=None,
            need_results=False,
            need_queryset=False,
            keys=None,
            related_obj: list = None,
            m_to_m_obj: list = None,
            related_mapping: dict = None,
            m_to_m_mapping: dict = None,
            **kwargs,
    ):
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
        results, queryset, current_page_queryset = self.find(obj, request.GET.dict(), obj_serializer)

        try:
            if not related_obj:
                related_obj, related_mapping = self.injection_related_data('GET')
            if not m_to_m_obj:
                m_to_m_obj, m_to_m_mapping = self.injection_m_to_m_data('GET')
            if results.data and results.data.result and related_mapping and related_obj:
                result = self.extend_result_field(
                    obj_serializer, related_obj, m_to_m_obj, related_mapping, m_to_m_mapping, current_page_queryset
                )
                results.data.result = result
        except Exception as e:
            get_error_status_code(e, results)
        if need_results:
            return results
        return RESTResponse(results)

    def post(
            self,
            request,
            obj,
            obj_serializer,
            data=None,
            need_results=False,
            related_obj: list = None,
            m_to_m_obj: list = None,
            related_mapping=None,
            m_to_m_mapping=None,
            **kwargs,
    ):
        results = Results()
        if not data:
            data = request.data
        if data.get("data"):
            data = data.get("data")
        serializer = obj_serializer(data=data)
        if not related_obj:
            related_obj, related_mapping = self.injection_related_data('POST')
        if not m_to_m_obj:
            m_to_m_obj, m_to_m_mapping = self.injection_m_to_m_data('POST')
        self.execute_related_extend(related_obj, related_mapping, data)
        self.execute_m_to_m_extend(m_to_m_obj, m_to_m_mapping, data)
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

    def execute_related_extend(self, related_obj, related_mapping, data):
        if related_obj and related_mapping:
            for obj in related_obj:
                obj_name = obj.__name__.lower()
                obj_mapping = related_mapping.get(obj_name)
                if not obj_mapping:
                    raise Exception(f"{obj_name}  are not mapping!!!")
                queryset = self.get_relevance_queryset(obj, obj_name, data)
                self.extend_relevance_data(data, queryset, obj_mapping)

    def execute_m_to_m_extend(self, m_to_m_obj, m_to_m_mapping, data):
        pass

    def extend_relevance_data(self, data, queryset, obj_mapping):
        if queryset:
            value = getattr(queryset, obj_mapping[0], None)
            if value is not None:
                data[obj_mapping[1]] = value

    def get_relevance_orm_q(self, obj_name, data):
        conditions = {}
        for item, value in data.items():
            if obj_name + "__" in item:
                conditions[item.replace(obj_name + "__", "")] = value
        if conditions:
            orm_q = self.get_orm_q(conditions)
            return orm_q

    def get_relevance_queryset(self, obj, obj_name, data):
        orm_q = self.get_relevance_orm_q(obj_name, data)
        queryset = obj.objects.filter(orm_q).first()
        return queryset

    def extend_result_field(self, obj_serializer, related_obj, m_to_m_obj, related_mapping, m_to_m_mapping, queryset):
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
            self.extend_related_field(item, item_result, related_obj, related_mapping)
            result.append(item_result)
        return result

    def extend_m_to_m_field(self, item, item_result, m_to_m_obj, m_to_m_mapping):
        for obj in m_to_m_obj:
            m_to_m_name = obj.__name__.lower()
            item_result[m_to_m_name] = []
            m_to_m = getattr(item, m_to_m_name).all()
            mapping = m_to_m_mapping[m_to_m_name]
            for instance in m_to_m:
                for key in mapping:
                    value = getattr(instance, mapping[key])
                    if value:
                        item_result[key].append(value)

    def extend_related_field(self, item, item_result, related_obj, related_mapping):
        for obj in related_obj:
            # 获取关联表
            related_name = obj.__name__.lower()
            # 获取queryset中的外键对象
            related_instance = getattr(item, related_name)
            # 对结果集进行字段扩展
            mapping = related_mapping[related_name]
            for key in mapping:
                child_obj = related_instance
                if child_obj:
                    # 多级 关联
                    if "." in mapping[key]:
                        attrs = mapping[key].split(".")
                        # 多级 关联的外键对象
                        child_obj = getattr(related_instance, attrs[0])
                        for attr in attrs[1:]:
                            child_obj = getattr(child_obj, attr)
                        item_result[key] = child_obj
                    else:
                        item_result[key] = getattr(related_instance, mapping[key], None)
                else:
                    item_result[key] = None

    def get_queryset(self, obj, data) -> (QuerySet, QuerySet):

        drop_group = data.get(self.CHOOSE_GROUP)
        queryset, extend_queryset = super().get_queryset(obj, data)
        if drop_group:
            group = tuple(drop_group.split(","))
            extend_queryset = queryset.values(*group).annotate(count=Count("id"))
        return queryset, extend_queryset

    def extend_page_type_results(self, data, page_type_results, extend_queryset, *args, **kwargs):
        if extend_queryset:
            page_type_results.group = list(extend_queryset)

    def injection_related_data(self, method):
        related_obj = None
        related_mapping = None
        return related_obj, related_mapping

    def injection_m_to_m_data(self, method):
        m_to__obj = None
        m_to__mapping = None
        return m_to__obj, m_to__mapping
