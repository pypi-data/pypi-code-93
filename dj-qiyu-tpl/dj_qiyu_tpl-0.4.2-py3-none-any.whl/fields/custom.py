from django.forms import CharField, BoundField, Form
from django.template import loader
from django.utils.safestring import mark_safe

__all__ = ["CustomFormField", "CustomBoundField"]


class CustomBoundField(BoundField):
    field_template = "dj_qiyu_tpl/fields/custom.html"

    def __init__(self, form: Form, field: "CustomFormField", name: str):
        super().__init__(form, field, name)

    def as_widget(self, widget=None, attrs=None, only_initial=False) -> str:
        context = {
            "form": self.form,
            "field": self.field,
            "name": self.name,
            "type": self.field.widget.input_type,
            "widget": self.field.widget,
        }
        html = loader.render_to_string(self.field_template, context=context)
        return mark_safe(html)


class CustomFormField(CharField):
    bound_field_type = CustomBoundField

    def get_bound_field(self, form, field_name) -> CustomBoundField:
        return self.bound_field_type(form, self, field_name)
