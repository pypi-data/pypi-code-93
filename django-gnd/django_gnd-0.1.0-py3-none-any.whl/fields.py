from django.db import models

from . forms import GndFormField


class GndField(models.CharField):

    description = "A Field for a GND Identifier"

    def formfield(self, **kwargs):
        defaults = {
            'form_class': GndFormField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 250
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs
