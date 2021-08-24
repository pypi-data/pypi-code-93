"""
widgets.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/1/21 1:58 PM
"""

import json
from inspect import isfunction

from django.forms import Widget, Media
from django.urls import reverse, NoReverseMatch

from ..kelove_settings import JSONFieldSettings, CkfinderFieldSettings, EditorMdFieldSettings, EditorCkFieldSettings


class BaseWidget(Widget):
    """
    表单组件基类
    """

    def __init__(self, attrs=None):
        self.attrs = attrs if isinstance(attrs, dict) else {}
        self.field_settings = self.get_field_settings(
            field_settings=self.attrs.get('field_settings', {})
        )
        attrs['field_settings'] = json.dumps(self.field_settings)
        super().__init__(attrs)

    @classmethod
    def get_field_settings(cls, field_settings=None) -> dict:
        """
        配置信息统一获取
        :param field_settings:
        :return:
        """

        if isfunction(field_settings):
            field_settings = field_settings()

        return dict({} if not isinstance(field_settings, dict) else {
            k: (v() if isfunction(v) else v)
            for k, v
            in field_settings.items()
        })


class JSONWidget(BaseWidget):
    """
    JSON 表单组件
    https://github.com/josdejong/jsoneditor
    """

    template_name = 'kelove_database/forms/json.html'

    @classmethod
    def get_field_settings(cls, field_settings=None) -> dict:
        """
        配置信息统一获取
        :param field_settings:
        :return:
        """

        return {
            **JSONFieldSettings.get(),
            **super().get_field_settings(field_settings=field_settings)
        }

    def format_value(self, value):
        if value == '' or value is None:
            return None
        if not isinstance(value, str):
            value = json.dumps(value)
        return value

    def _get_media(self):
        return Media(
            css={
                "all": (
                    'kelove_database/jsoneditor/jsoneditor.min.css',
                    'kelove_database/jsoneditor/style.css',
                )
            },
            js=(
                'kelove_database/jsoneditor/jsoneditor.min.js',
                'kelove_database/jsoneditor/script.js',
            )
        )

    media = property(_get_media)


class CkFinderWidget(BaseWidget):
    """
    CkFinder 文件选择器 表单组件
    """

    default_field_settings = {
        'chooseFiles': True,
        'plugins': ['ClearCache'],
    }

    template_name = 'kelove_database/forms/ckfinder.html'

    IMAGE_EXT = ['png', 'jpg', 'gif', 'ico', 'jpeg', 'svg', 'bmp']

    @classmethod
    def get_field_settings(cls, field_settings=None) -> dict:
        """
        重构，添加上传路经处理
        :param field_settings:
        :return:
        """

        field_settings = {
            **cls.default_field_settings,
            **CkfinderFieldSettings.get_client_settings(),
            **super().get_field_settings(field_settings=field_settings)
        }

        connector_path = field_settings['connectorPath']
        try:
            connector_path = reverse(connector_path)
        except NoReverseMatch:
            pass

        field_settings['connectorPath'] = connector_path

        if 'license_key' in field_settings.keys():
            field_settings.pop('license_key')

        if 'license_name' in field_settings.keys():
            field_settings.pop('license_name')

        return field_settings

    def _get_media(self):
        return Media(
            css={
                "all": (
                    'kelove_database/ckfinder/style.css',
                )
            },
            js=(
                'kelove_database/ckfinder/ckfinder.js',
                'kelove_database/ckfinder/script.js',
            )
        )

    media = property(_get_media)


class EditorMdWidget(BaseWidget):
    """
    EditorMd 表单组件
    https://github.com/pandao/editor.md
    """

    # Markdown编辑器 字段配置
    # 添加以下配置，化身代码编辑器
    # 'watch': False,
    # 'toolbar': False,
    # 'mode': 'python'
    # 可选语言：
    #  text/html
    #  javascript
    #  php
    #  text/xml
    #  text/json
    #  clike
    #  javascript
    #  perl
    #  go
    #  python
    #  clike
    #  css
    #  ruby
    #
    default_field_settings = {
        'imageUpload': False,
        'imageUploadURL': '',
        'readOnly': False,
        'theme': '',
        'previewTheme': 'default',
        'editorTheme': 'default',
        'autoFocus': False,
        'toolbarAutoFixed': False,
        'emoji': True,
        'codeFold': True,
        'tocDropdown': True,
        'mode': 'markdown',
        'tocm': True,
        'height': 300,
        'width': '100%',
    }

    template_name = 'kelove_database/forms/editor_md.html'

    @classmethod
    def get_field_settings(cls, field_settings=None) -> dict:
        """
        重构，添加上传路经处理
        :param field_settings:
        :return:
        """

        field_settings = {
            **cls.default_field_settings,
            **EditorMdFieldSettings.get(),
            **super().get_field_settings(field_settings=field_settings)
        }

        if ('imageUpload' not in field_settings) or ('imageUploadURL' not in field_settings):
            return field_settings

        image_upload_url = field_settings['imageUploadURL']

        if isinstance(image_upload_url, dict):
            image_upload_url = CkFinderWidget.get_field_settings(image_upload_url)
        else:
            image_upload_url = str(image_upload_url)
            try:
                image_upload_url = reverse(image_upload_url)
            except NoReverseMatch:
                pass

        field_settings['imageUploadURL'] = image_upload_url
        return field_settings

    def _get_media(self):
        return Media(
            css={
                "all": (
                    'kelove_database/editor_md/css/editormd.min.css',
                    'kelove_database/editor_md/style.css',
                )
            },
            js=(
                'kelove_database/jquery/jquery-3.5.1.min.js',
                'kelove_database/editor_md/editormd.min.js',
                'kelove_database/ckfinder/ckfinder.js',
                'kelove_database/editor_md/script.js',
            )
        )

    media = property(_get_media)


class EditorCkWidget(BaseWidget):
    """
    CkEditor 表单组件
    """

    default_field_settings = {
        'image': {
            'toolbar': [
                'imageTextAlternative',
                'imageStyle:full',
                'imageStyle:side',
                'linkImage'
            ]
        },
        'table': {
            'contentToolbar': [
                'tableColumn',
                'tableRow',
                'mergeTableCells',
                'tableCellProperties',
                'tableProperties'
            ]
        },
        'language': 'zh-cn',
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
                {'model': 'heading4', 'view': 'h4', 'title': 'Heading 4', 'class': 'ck-heading_heading4'},
                {'model': 'heading5', 'view': 'h5', 'title': 'Heading 5', 'class': 'ck-heading_heading5'},
                {'model': 'heading6', 'view': 'h6', 'title': 'Heading 6', 'class': 'ck-heading_heading6'},
            ]
        }
    }

    template_name = 'kelove_database/forms/ckeditor.html'

    @classmethod
    def get_field_settings(cls, field_settings=None) -> dict:
        """
        重构，添加上传路经处理
        :param field_settings:
        :return:
        """

        field_settings = {
            **cls.default_field_settings,
            **EditorCkFieldSettings.get(),
            **super().get_field_settings(field_settings=field_settings)
        }

        if 'ckfinder' not in field_settings:
            ckfinder_settings = {}
        else:
            ckfinder_settings = dict(field_settings.get('ckfinder', {}))

        if 'options' not in ckfinder_settings:
            ckfinder_settings_options = {}
        else:
            ckfinder_settings_options = dict(ckfinder_settings.get('options', {}))
        ckfinder_settings_options = CkFinderWidget.get_field_settings(ckfinder_settings_options)
        ckfinder_settings['options'] = ckfinder_settings_options
        ckfinder_settings['openerMethod'] = 'modal'
        field_settings['ckfinder'] = ckfinder_settings
        return field_settings

    def _get_media(self):
        return Media(
            css={
                "all": (
                    'kelove_database/ckeditor/style.css',
                )
            },
            js=(
                'kelove_database/ckeditor/build/ckeditor.js',
                'kelove_database/ckfinder/ckfinder.js',
                'kelove_database/ckeditor/script.js',
            )
        )

    media = property(_get_media)
