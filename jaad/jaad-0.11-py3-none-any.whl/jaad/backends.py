from django.utils.datastructures import OrderedSet

from django_filters import compat
from django_filters.rest_framework import filterset
from rest_framework.filters import BaseFilterBackend
from rest_framework.schemas import AutoSchema

from jaad.forms import fields as jaad_fields

JSON_FIELD_TYPE = "json_field_type"


class JaadBackend(BaseFilterBackend):
    default_filter_set = filterset.FilterSet

    @staticmethod
    def _get_field_type(field):
        if hasattr(field.__class__, JSON_FIELD_TYPE):
            return getattr(field.__class__, JSON_FIELD_TYPE)
        else:
            return "string"

    def filter_queryset(self, request, queryset, view):
        raise NotImplementedError("This backend does not support filter_queryset().")

    def to_html(self, request, queryset, view):
        raise NotImplementedError("This backend does not support to_html().")

    def get_schema_fields(self, view):
        # This is not compatible with widgets where the query param differs from the
        # filter's attribute name. Notably, this includes `MultiWidget`, where query
        # params will be of the format `<name>_0`, `<name>_1`, etc...
        assert (
            compat.coreapi is not None
        ), "coreapi must be installed to use `get_schema_fields()`"
        custom_renderers = getattr(view, "renderer_classes", [])
        supported_formats = [
            (
                renderer.format,
                renderer.format_description
                if hasattr(renderer, "format_description")
                else renderer.format,
            )
            for renderer in custom_renderers
        ]

        custom_fields = []

        if len(supported_formats) > 0:
            format_field = jaad_fields.ChoiceField(
                required=False, choices=supported_formats, help_text="Response format."
            )
            jaad_fields.set_field_default_value(format_field, supported_formats[0][0])
            custom_fields.append(("format", format_field))

        return self.format_fields(custom_fields)

    def get_method_schema_fields(self, view, method_name):
        method = getattr(view, method_name.lower(), None)

        if method is None:
            return []

        custom_get_parameters = getattr(method, "custom_parameters", {}).get("get", [])

        method_fields = []
        for parameter_form_definition in custom_get_parameters:
            method_fields += parameter_form_definition().declared_fields.items()

        return self.format_fields(method_fields)

    def format_fields(self, custom_fields):
        return [
            compat.coreapi.Field(
                name=field_name,
                required=False,
                location="query",
                description=field.help_text,
                type=self._get_field_type(field),
                example=None,
                schema=None,
            )
            for field_name, field in OrderedSet(custom_fields)
        ]


class JaadSchema(AutoSchema):
    def get_filter_fields(self, path, method):
        if not self._allows_filters(path, method):
            return []

        fields = []
        for filter_backend in self.view.filter_backends:
            if hasattr(filter_backend, "get_method_schema_fields"):
                fields += filter_backend().get_method_schema_fields(self.view, method)
            fields += filter_backend().get_schema_fields(self.view)
        return fields
