from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils.module_loading import import_string
from rest_framework import serializers
from rest_framework.utils.humanize_datetime import humanize_strptime

from dj_dynamic_settings.metadata import SimpleMetadata


class BaseValidator(object):
    @property
    def detail(self):
        raise NotImplementedError


class TypeValidator(BaseValidator):
    message = "'{value}' is not valid. Valid types are {types}."
    label_lookup = {
        "bool": "boolean",
        "str": "string",
        "unicode": "string",
        "bytes": "string",
        "int": "integer",
        "float": "float",
        "Decimal": "decimal",
        "dict": "nested object",
        "list": "list",
        "newstr": "string",
        "newlist": "list",
        "newint": "int",
        "newbytes": "string",
        "newdict": "nested object",
    }

    def __init__(self, *types):
        assert types, "At least one class has to be provided."
        self.types = types

    def __call__(self, value):
        if not isinstance(value, self.types):
            types = ", ".join(
                self.label_lookup.get(t.__name__, t.__name__) for t in self.types
            )
            raise ValidationError(self.message.format(value=value, types=types))

    @property
    def detail(self):
        return {
            "types": [self.label_lookup.get(t.__name__, t.__name__) for t in self.types]
        }


class ModulePathValidator(BaseValidator):
    message = "{path} not a valid module path."

    def __call__(self, value):
        try:
            import_string(value)
        except ImportError:
            raise ValidationError(self.message.format(path=value))

    @property
    def detail(self):
        return {"types": ["module_path"]}


class DateTimeValidator(BaseValidator):
    message = "DateTime format does not match. DateTime: {value} Format: {dformat}"

    def __init__(self, date_time_format):
        assert date_time_format, "Datetime format has to be provided."
        self.date_time_format = date_time_format

    def __call__(self, value):
        try:
            datetime.strptime(value, self.date_time_format)
        except ValueError:
            date_time_format = humanize_strptime(self.date_time_format)
            raise ValidationError(
                self.message.format(value=value, dformat=date_time_format)
            )

    @property
    def detail(self):
        return {
            "types": ["datetime"],
            "format": humanize_strptime(self.date_time_format),
        }


class SerializerValidator(BaseValidator):
    def __init__(self, serializer_class, serializer_kwargs=None):
        self.serializer_class = serializer_class
        self.serializer_kwargs = serializer_kwargs

    def get_serializer_kwargs(self):
        serializer_kwargs = self.serializer_kwargs or {}
        if callable(serializer_kwargs):
            serializer_kwargs = serializer_kwargs()
        assert "data" not in serializer_kwargs
        assert "instance" not in serializer_kwargs
        return serializer_kwargs

    def __call__(self, value):
        serializer = self.serializer_class(data=value, **self.get_serializer_kwargs())
        serializer.is_valid(raise_exception=True)

    @property
    def detail(self):
        meta = SimpleMetadata()
        serializer = self.serializer_class(**self.get_serializer_kwargs())
        params = {}
        if isinstance(serializer, serializers.ListSerializer):
            params["types"] = [TypeValidator.label_lookup.get("list")]
            if isinstance(serializer.child, serializers.Serializer):
                params["fields"] = meta.get_serializer_info(serializer)
            else:
                params["field"] = meta.get_field_info(serializer.child)
        else:
            params["types"] = [TypeValidator.label_lookup.get("dict")]
            params["fields"] = meta.get_serializer_info(serializer)
        return params
