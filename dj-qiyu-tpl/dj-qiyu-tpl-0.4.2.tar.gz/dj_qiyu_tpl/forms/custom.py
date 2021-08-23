from django.forms import Form
from django.template import loader
from django.utils.safestring import mark_safe

__all__ = ["CustomForm"]


class CustomForm(Form):
    """
    自定义的 Form
    """

    custom_p_template = "dj_qiyu_tpl/forms/custom_p.html"
    custom_table_template = "dj_qiyu_tpl/forms/custom_table.html"
    custom_ul_template = "dj_qiyu_tpl/forms/custom_ui.html"

    def as_p(self):
        return self._do_render(self.custom_p_template)

    def as_table(self):
        return self._do_render(self.custom_table_template)

    def as_ul(self):
        return self._do_render(self.custom_ul_template)

    def _do_render(self, tpl: str) -> str:
        ctx = self._get_render_context()
        return mark_safe(loader.render_to_string(tpl, ctx))

    def _get_render_context(self) -> dict:
        """
        render context have form and fields

        form   is subclass of form
        fields is CustomBoundField
        """
        ctx = {"form": self, "fields": dict()}
        for name, field in self.fields.items():
            bf = field.get_bound_field(self, name)
            ctx["fields"][name] = bf
        return ctx
