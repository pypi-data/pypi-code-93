from django.db import models
from rest_framework.fields import empty
from rest_framework.metadata import SimpleMetadata as _SimpleMetadata

from dj_dynamic_settings.registry import Unset


class SimpleMetadata(_SimpleMetadata):
    def get_field_info(self, field):
        field_info = super(SimpleMetadata, self).get_field_info(field)
        if hasattr(field, "default"):
            default = field.default
            if default is empty:
                default = Unset.__name__
            if callable(default):
                default = default()
            if isinstance(default, models.Model):
                default = default.pk
            field_info["default"] = default

        if "input_type" in field.style:
            field_info["type"] = field.style["input_type"]
        return field_info
