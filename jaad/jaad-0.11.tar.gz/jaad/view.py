from functools import wraps

from django.http import HttpResponse
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from jaad.backends import JaadBackend, JaadSchema
from jaad.renderers import PrettyJsonRenderer, CSVRenderer


def with_parameters(method, *parameter_forms):
    def wrapper(handler):
        if not hasattr(handler, "custom_parameters"):
            handler.custom_parameters = {}
        handler.custom_parameters[method.lower()] = parameter_forms
        return handler

    return wrapper


def _wrap_view_query_handler(handler):
    @wraps(handler)
    def wrapper(request):
        custom_get_parameters = getattr(handler, "custom_parameters", {}).get("get", [])

        request.GET.current_user = request.user

        get_parameters_filled_forms = [
            parameter_form_definition(data=request.GET)
            for parameter_form_definition in custom_get_parameters
        ]

        if not all(form.is_valid() for form in get_parameters_filled_forms):
            errors = {}
            for form in get_parameters_filled_forms:
                errors.update(form.errors)
            raise ValidationError(detail=errors)

        parameters_values = [form.clean() for form in get_parameters_filled_forms]
        result = handler(request, *parameters_values)
        return Response(result) if not isinstance(result, HttpResponse) else result

    return wrapper


class JaadView(APIView):
    renderer_classes = (PrettyJsonRenderer, CSVRenderer)
    filter_backends = (JaadBackend,)
    activate_if_conditions = []
    schema = JaadSchema()

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

    def __getattribute__(self, item):
        return super().__getattribute__(item)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for request_type in self.http_method_names:
            if hasattr(self, request_type):
                new_handler = _wrap_view_query_handler(getattr(self, request_type))
                setattr(self, request_type, new_handler)
