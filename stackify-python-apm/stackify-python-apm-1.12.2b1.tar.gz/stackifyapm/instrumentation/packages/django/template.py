from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils import get_method_name


class DjangoTemplateInstrumentation(AbstractInstrumentedModule):
    name = "django_template"

    instrument_list = [("django.template", "Template.render")]

    def call(self, module, method, wrapped, instance, args, kwargs):
        context = {
            "CATEGORY": "Template",
            "SUBCATEGORY": get_method_name(method).title(),
            "COMPONENT_CATEGORY": "Template",
            "COMPONENT_DETAIL": "Template",
            "TEMPLATE": getattr(instance, "name", None) or "<template string>",
        }

        with CaptureSpan("template.django", context):
            return wrapped(*args, **kwargs)


class DjangoTemplateSourceInstrumentation(AbstractInstrumentedModule):
    name = "django_template_source"
    instrument_list = [("django.template.base", "Parser.extend_nodelist")]

    def call(self, module, method, wrapped, instance, args, kwargs):
        ret = wrapped(*args, **kwargs)

        if len(args) > 1:
            node = args[1]
        elif "node" in kwargs:
            node = kwargs["node"]
        else:
            return ret

        if len(args) > 2:
            token = args[2]
        elif "token" in kwargs:
            token = kwargs["token"]
        else:
            return ret

        if not hasattr(node, "token") and hasattr(token, "lineno"):
            node.token = token

        return ret
