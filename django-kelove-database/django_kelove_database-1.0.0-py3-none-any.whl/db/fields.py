"""
fields.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/1/21 3:06 PM
"""

from django.db.models import (
    JSONField as BaseJSONField,
    CharField as BaseCharField,
    TextField as BaseTextField,
)

from ..forms import fields


class JSONField(BaseJSONField):
    """
    JSON 编辑器字段
    """

    def __init__(self, field_settings=None, default=dict, **kwargs):
        self.field_settings = field_settings
        super().__init__(default=default, **kwargs)

    def formfield(self, **kwargs):
        kwargs['form_class'] = fields.JSONField
        kwargs['field_settings'] = self.field_settings
        return super().formfield(**kwargs)


class CkFinderField(BaseCharField):
    """
    CkFinder 文件选择器字段
    """

    description = 'CkFinder'

    def __init__(self, field_settings=None, **kwargs):
        self.field_settings = field_settings
        super().__init__(**kwargs)

    def formfield(self, **kwargs):
        kwargs['form_class'] = fields.CkFinderField
        kwargs['field_settings'] = self.field_settings
        return super().formfield(**kwargs)


class EditorMdField(BaseTextField):
    """
    Markdown 编辑器字段
    """

    description = 'MarkdownEditor'

    def __init__(self, field_settings=None, **kwargs):
        self.field_settings = field_settings
        super().__init__(**kwargs)

    def formfield(self, **kwargs):
        kwargs['form_class'] = fields.EditorMdField
        kwargs['field_settings'] = self.field_settings
        return super().formfield(**kwargs)


class EditorCkField(BaseTextField):
    """
    Ckeditor 编辑器字段
    """

    description = 'Ckeditor'

    def __init__(self, field_settings=None, **kwargs):
        self.field_settings = field_settings
        super().__init__(**kwargs)

    def formfield(self, **kwargs):
        kwargs['form_class'] = fields.EditorCkField
        kwargs['field_settings'] = self.field_settings
        return super().formfield(**kwargs)
