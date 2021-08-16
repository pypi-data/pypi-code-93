# -*- coding: utf-8 -*-
# @Time    : 2019-09-11 17:17
# @Author  : xzr
# @File    : schema
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :
import copy
from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.errors import SwaggerGenerationError
from drf_yasg.inspectors.field import FieldInspector
from drf_yasg.inspectors.view import SwaggerAutoSchema
from drf_yasg.utils import force_serializer_instance, guess_response_status, no_body, param_list_to_odict
from rest_framework import serializers, status
from rest_framework.relations import ManyRelatedField, RelatedField

from .filters import MyFilterSerializer
from .response import RspError, RspErrorEnum, RspSerializer

api_info = openapi.Info(
        title="Myadmin API",
        default_version='v1',
        description="Myadmin description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License")
)



def compose_enum_description(enum_item_list):
    return '\n'.join([' * `%s` - %s  ' % (k, v) for k, v in enum_item_list])


class CustomChoicesFieldInspector(FieldInspector):
    """
    自定选择列表字段描述检测器
    """

    def process_result(self, result, method_name, obj, **kwargs):
        serializer = obj

        # 增加 枚举描述提示,关联模型不执行
        if isinstance(serializer, (ManyRelatedField, RelatedField)):
            return result
        choices_attr = getattr(serializer, 'choices', None)
        if choices_attr:
            enum_item_list = list(serializer.choices.items())


            if not hasattr(result, 'has_add_enum_desc'):
                choices_text = compose_enum_description(enum_item_list)
                setattr(result, 'description', '%s\n%s ' % (getattr(result, 'description', ''), choices_text))
                setattr(result, 'has_add_enum_desc', True)
        return result


class CustomSwaggerAutoSchema(SwaggerAutoSchema):

    def __init__(self, view, path, method, components, request, overrides, operation_keys=None):
        overrides['field_inspectors'] = [CustomChoicesFieldInspector]
        # overrides['filter_inspectors'] = [CustomChoicesFieldInspector]

        super(CustomSwaggerAutoSchema, self).__init__(view, path, method, components, request, overrides,
                                                      operation_keys)

    def get_operation(self, operation_keys=None):
        # 只返回有 swagger_auto_schema 装饰器的方法
        action = getattr(self.view, 'action', self.method.lower())
        action_method = getattr(self.view, action, None)
        has_decorator_swagger_auto_schema = getattr(action_method, '_swagger_auto_schema', None)
        if not has_decorator_swagger_auto_schema:
            return None
        # 只有设置了参数才返回
        if self.get_query_serializer() or self.get_request_serializer():
            return super(CustomSwaggerAutoSchema, self).get_operation(operation_keys)

    def get_responses(self):
        """Get the possible responses for this view as a swagger :class:`.Responses` object.

        :return: the documented responses
        :rtype: openapi.Responses
        """
        response_serializers = self.get_response_serializers()
        return openapi.Responses(
                responses=self.get_response_schemas(response_serializers)
        )

    def get_operation_id(self, operation_keys=None):
        """Return an unique ID for this operation. The ID must be unique across
        all :class:`.Operation` objects in the API.

        :param tuple[str] operation_keys: an array of keys derived from the pathdescribing the hierarchical layout
            of this view in the API; e.g. ``('snippets', 'list')``, ``('snippets', 'retrieve')``, etc.
        :rtype: str
        """
        operation_keys = operation_keys or self.operation_keys
        #  operation_keys = operation_keys[:3]
        # if getattr(self.view, 'is_api_view', False):
        #    operation_keys.pop()
        #    # operation_keys.append('- %s' % self.method.lower())
        operation_id = self.overrides.get('operation_id', '')
        if not operation_id:
            # operation_id = '/'.join(sort_set_list(operation_keys))
            operation_id = self.path
            # operation_id += ' [%s]' % self.method.lower()
        return operation_id

    def get_view_action(self):
        return getattr(self.view, 'action', '')

    def get_view_annotations(self):
        action_func = self.view
        action_name = self.get_view_action()
        if action_name:
            action_func = getattr(self.view, action_name)
        view_annotations = getattr(action_func, '__annotations__', {})

        return view_annotations

    def get_view_annotations_serializer(self, key):
        serializer = self.get_view_annotations().get(key, None)
        if serializer:
            return force_serializer_instance(serializer)
        return serializer

    def get_request_serializer(self):
        """Return the request serializer (used for parsing the request payload) for this endpoint.

        :return: the request serializer, or one of :class:`.Schema`, :class:`.SchemaRef`, ``None``
        :rtype: rest_framework.serializers.Serializer
        """

        params_serializer = self.get_view_annotations_serializer('params')
        body_override = self._get_request_body_override() or params_serializer
        #  return body_override
        # if body_override is None and self.method in self.implicit_body_methods:
        #    return self.get_view_serializer()

        if body_override is no_body:
            return None

        return body_override

    def get_query_serializer(self):
        """Return the query serializer (used for parsing query parameters) for this endpoint.

        :return: the query serializer, or ``None``
        """
        params_serializer = self.get_view_annotations_serializer('params')
        query_serializer = self.overrides.get('query_serializer', None) or params_serializer
        if query_serializer is not None:
            query_serializer = force_serializer_instance(query_serializer)
        return query_serializer

    def get_query_parameters(self):
        """Return the query parameters accepted by this view.

        :rtype: list[openapi.Parameter]
        """

        natural_parameters = self.get_filter_parameters() + self.get_pagination_parameters()

        # natural_parameters = []

        query_serializer = self.get_query_serializer()

        serializer_parameters = []

        if query_serializer is not None and not isinstance(query_serializer, MyFilterSerializer):
            serializer_parameters = self.serializer_to_parameters(query_serializer, in_=openapi.IN_QUERY)
            # if serializer_parameters:
            return serializer_parameters
            if len(set(param_list_to_odict(natural_parameters)) & set(param_list_to_odict(serializer_parameters))) != 0:
                raise SwaggerGenerationError(
                        "your query_serializer contains fields that conflict with the "
                        "filter_backend or paginator_class on the view - %s %s" % (self.method, self.path)
                )

        return natural_parameters + serializer_parameters

    def get_response_serializers(self):
        """Return the response codes that this view is expected to return, and the serializer for each response body.
        The return value should be a dict where the keys are possible status codes, and values are either strings,
        ``Serializer``\\ s, :class:`.Schema`, :class:`.SchemaRef` or :class:`.Response` objects. See
        :func:`@swagger_auto_schema <.swagger_auto_schema>` for more details.

        :return: the response serializers
        :rtype: dict
        """

        manual_responses = self.overrides.get('responses', None) or self.get_view_annotations_serializer('return')
        if not isinstance(manual_responses, dict):
            manual_responses = {status.HTTP_200_OK: manual_responses}
        responses = OrderedDict(
                (str(sc), self.generate_rsp_serializer_schema(resp)) for sc, resp in manual_responses.items())

        return responses

    def generate_rsp_serializer_schema(self, rsp_data_serializer: serializers.Field = None):
        """
        生成最终 rsp 结果,添加 错误代码描述
        :param rsp_serializer:
        :return:
        """

        if rsp_data_serializer:
            rep_code_errors:RspErrorEnum = getattr(rsp_data_serializer, 'Errors', None)
            default_declared_fields = RspSerializer._declared_fields
            rep_code_serializer = default_declared_fields['code']
            choices = rep_code_serializer.choices
            # 增加错误代码
            if rep_code_errors and (
                    issubclass(rep_code_errors, RspErrorEnum) or isinstance(rep_code_errors, RspErrorEnum)):
                rsp_err_code_member_list = rep_code_errors.member_list()
                choices = copy.copy(rep_code_serializer.choices)
                choices.update(rsp_err_code_member_list)
            choices = list(choices.items())
            rsp_code_schema = self.serializer_to_schema(
                    serializers.ChoiceField(label=rep_code_serializer.label, choices=choices))
            rsp_data_serializer = force_serializer_instance(rsp_data_serializer)
        else:
            rsp_code_schema = self.serializer_to_schema(RspSerializer._declared_fields['code'])
            rsp_data_serializer = RspSerializer._declared_fields['data']

        default_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict(
                    (
                        ('code', rsp_code_schema),
                        ('msg', self.serializer_to_schema(RspSerializer._declared_fields['msg'])),
                        ('data', self.serializer_to_schema(rsp_data_serializer))
                )
                ),
                required=['code', 'msg']
        )

        return default_schema

    def _get_default_responses(self):
        """Get the default responses determined for this view from the request serializer and request method.

        :type: dict[str, openapi.Schema]
        """
        method = self.method.lower()

        default_status = guess_response_status(method)

        default_schema = self.get_default_response_serializer()

        default_schema = default_schema or ''
        if default_schema and not isinstance(default_schema, openapi.Schema):
            default_schema = self.serializer_to_schema(default_schema) or ''

        if default_schema and self.get_view_action() not in ('edit'):
            if self.has_list_response():
                default_schema = openapi.Schema(type=openapi.TYPE_ARRAY, items=default_schema)
            if self.should_page():
                query_schema = self.get_query_serializer() or serializers.DictField(help_text="查询条件", required=False)
                paged_schema = openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties=OrderedDict((
                                ('count', openapi.Schema(type=openapi.TYPE_INTEGER)),
                                ('page', openapi.Schema(type=openapi.TYPE_INTEGER)),
                                ('page_size', openapi.Schema(type=openapi.TYPE_INTEGER)),

                                ('next',
                                 openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, x_nullable=True)),
                                ('previous',
                                 openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, x_nullable=True)),
                                ('results', default_schema),
                                ('filter', self.serializer_to_schema(query_schema)),
                        )),
                        required=['results']
                )
                default_schema = paged_schema

        rsp_code_schema = self.serializer_to_schema(RspSerializer._declared_fields['code'])

        default_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                        ('code', rsp_code_schema),
                        ('msg', self.serializer_to_schema(RspSerializer._declared_fields['msg'])),
                        ('data', default_schema)
                )
                ),
                required=['code', 'msg']
        )

        return OrderedDict({str(default_status): default_schema})
