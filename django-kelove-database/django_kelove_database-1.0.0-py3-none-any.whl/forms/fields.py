"""
fields.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/1/21 3:04 PM
"""

from django.forms.fields import (
    JSONField as BaseJSONField,
    CharField as BaseCharField,
)

from . import widgets


class JSONField(BaseJSONField):
    """
    JSON 表单字段
    """

    def __init__(self, *, field_settings=None, **kwargs):
        self.field_settings = field_settings
        kwargs['widget'] = widgets.JSONWidget(attrs={'field_settings': field_settings})
        super().__init__(**kwargs)


class CkFinderField(BaseCharField):
    """
    CkFinder 文件选择器表单字段
    """

    def __init__(self, *, field_settings=None, **kwargs):
        self.field_settings = field_settings
        kwargs['widget'] = widgets.CkFinderWidget(attrs={'field_settings': field_settings})
        super().__init__(**kwargs)


class EditorMdField(BaseCharField):
    """
    Markdown 编辑器 表单字段
    """

    def __init__(self, *, field_settings=None, **kwargs):
        self.field_settings = field_settings
        kwargs['widget'] = widgets.EditorMdWidget(attrs={'field_settings': field_settings})
        super().__init__(**kwargs)


class EditorCkField(BaseCharField):
    """
    Ckeditor 编辑器 表单字段
    """

    def __init__(self, *, field_settings=None, **kwargs):
        self.field_settings = field_settings
        kwargs['widget'] = widgets.EditorCkWidget(attrs={'field_settings': field_settings})
        super().__init__(**kwargs)
