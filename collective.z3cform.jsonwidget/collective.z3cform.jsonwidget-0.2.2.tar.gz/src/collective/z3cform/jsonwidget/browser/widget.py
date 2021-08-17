# -*- coding: utf-8 -*-
from plone.restapi.types import utils
from z3c.form.browser import widget
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITextAreaWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IField
from z3c.relationfield.schema import RelationChoice
from plone import api

import json


class IJSONWidget(ITextAreaWidget):
    """ """


@implementer_only(IJSONWidget)
class JSONWidget(TextAreaWidget):
    """"""

    klass = u"json-textarea-widget"
    value = u""
    schema = None

    def update(self):
        super(JSONWidget, self).update()
        widget.addFieldClass(self)

    def json_data(self):
        data = super(JSONWidget, self).json_data()
        data["type"] = "textarea-json"
        return data

    def get_schema(self):
        fieldsets = utils.get_fieldsets(
            self.context, self.request, self.schema
        )
        schema_fieldsets = utils.get_fieldset_infos(fieldsets)
        # Build JSON schema properties
        properties = utils.get_jsonschema_properties(
            self.context, self.request, fieldsets
        )
        # Determine required fields
        required = []
        for field in utils.iter_fields(fieldsets):
            if field.field.required:
                required.append(field.field.getName())

        # Include field modes
        for field in utils.iter_fields(fieldsets):
            field_type = getattr(field.field, "value_type", "")
            field_name = field.field.getName()
            if isinstance(field_type, RelationChoice):
                properties[field_name]["items"]["type"] = "relation"
                properties[field_name]["items"]["root"] = "/".join(
                    api.portal.get().getPhysicalPath()
                )
            if field.mode:
                properties[field_name]["mode"] = field.mode

        return json.dumps(
            {
                "fields": properties,
                "required": required,
                "fieldsets": schema_fieldsets,
            }
        )


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def JSONFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, JSONWidget(request))
