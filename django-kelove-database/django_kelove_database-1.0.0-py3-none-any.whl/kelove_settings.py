"""
kelove_settings.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/1/21 2:09 PM
"""

from django.conf import settings
from django.forms import RadioSelect, CheckboxSelectMultiple
from django.utils.translation import gettext_lazy as _
from django import forms

from django_kelove_setting.setting_forms import Settings as SettingsForm

DATABASE_FIELD_JSON_MODES = ("code", "form", "text", "tree", "view", "preview")
DATABASE_FIELD_JSON_MODE_DEFAULT = "code"

KELOVE_DATABASE_FIELD_EDITOR_MD_MODES = (
    "markdown",
    "text/html",
    "javascript",
    "php",
    "text/xml",
    "text/json",
    "clike",
    "javascript",
    "perl",
    "go",
    "python",
    "clike",
    "css",
    "ruby",
)
KELOVE_DATABASE_FIELD_EDITOR_MD_MODE_DEFAULT = "markdown"

KELOVE_DATABASE_FIELD_EDITOR_MD_THEMES = (
    'default',
    '3024-day',
    '3024-night',
    'ambiance-mobile',
    'ambiance',
    'base16-dark',
    'base16-light',
    'blackboard',
    'cobalt',
    'colorforth',
    'eclipse',
    'elegant',
    'erlang-dark',
    'lesser-dark',
    'mbo',
    'mdn-like',
    'midnight',
    'monokai',
    'neat',
    'neo',
    'night',
    'paraiso-dark',
    'paraiso-light',
    'pastel-on-dark',
    'rubyblue',
    'solarized',
    'the-matrix',
    'tomorrow-night-bright',
    'tomorrow-night-eighties',
    'twilight',
    'vibrant-ink',
    'xq-dark',
    'xq-light',
    'zenburn'
)
KELOVE_DATABASE_FIELD_EDITOR_MD_THEME_DEFAULT = 'default'

KELOVE_DATABASE_FIELD_EDITOR_CK_TOOLBAR_DEFAULT = {
    'items': [
        'heading',
        '|',
        'bold',
        'italic',
        'link',
        'bulletedList',
        'numberedList',
        '|',
        'indent',
        'outdent',
        '|',
        # 'imageUpload',
        'imageInsert',
        'blockQuote',
        'insertTable',
        'mediaEmbed',
        'CKFinder',
        'alignment',
        '|',
        'code',
        'codeBlock',
        'exportPdf',
        'exportWord',
        'fontBackgroundColor',
        'fontColor',
        'fontSize',
        'fontFamily',
        'highlight',
        'horizontalLine',
        'htmlEmbed',
        'MathType',
        'ChemType',
        'removeFormat',
        'specialCharacters',
        'strikethrough',
        'subscript',
        'superscript',
        'todoList',
        'underline',
        '|',
        'undo',
        'redo'
    ]
}

KELOVE_DATABASE_FIELD_EDITOR_CK_PLUGINS = [
    "Alignment", "AutoImage", "Autoformat", "AutoLink", "Autosave", "BlockQuote", "Bold", "CKFinder",
    "CKFinderUploadAdapter", "Code", "CodeBlock", "Essentials", "ExportPdf", "ExportWord", "FontBackgroundColor",
    "FontColor", "FontFamily", "FontSize", "Heading", "Highlight", "HorizontalLine", "HtmlEmbed", "Image",
    "ImageCaption", "ImageInsert", "ImageResize", "ImageStyle", "ImageToolbar", "ImageUpload", "Indent",
    "IndentBlock", "Italic", "Link", "LinkImage", "List", "ListStyle", "Markdown", "MathType", "MediaEmbed",
    "MediaEmbedToolbar", "Mention", "Paragraph", "PasteFromOffice", "RemoveFormat", "SpecialCharacters",
    "Strikethrough", "Subscript",
    "Superscript", "Table", "TableCellProperties", "TableProperties", "TableToolbar", "TextTransformation",
    "Title", "TodoList", "Underline", "WordCount"
]


class JSONFieldSettings(SettingsForm):
    """
    JSON 字段配置
    """

    settings_title: str = _('字段配置 - JSON')

    mode = forms.ChoiceField(
        widget=RadioSelect,
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_JSON_MODE', DATABASE_FIELD_JSON_MODE_DEFAULT),
        required=False,
        label=_('默认显示类型'),
        choices=(
            (i, i) for i in DATABASE_FIELD_JSON_MODES
        )
    )

    modes = forms.MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_JSON_MODES', DATABASE_FIELD_JSON_MODES),
        required=False,
        label=_('可用显示类型'),
        choices=(
            (i, i) for i in DATABASE_FIELD_JSON_MODES
        )
    )

    @classmethod
    def get(cls) -> dict:
        data = super().get()
        data['allowed_modes'] = DATABASE_FIELD_JSON_MODES
        data['mode'] = data['mode'] if data['mode'] in DATABASE_FIELD_JSON_MODES else DATABASE_FIELD_JSON_MODE_DEFAULT
        modes = (i for i in data['modes'] if i in DATABASE_FIELD_JSON_MODES)
        modes = list(modes)
        data['modes'] = modes if modes else [DATABASE_FIELD_JSON_MODE_DEFAULT]
        return data


class CkfinderFieldSettings(SettingsForm):
    """
    Ckfinder 字段配置
    """

    settings_title: str = _('字段配置 - Ckfinder')

    get_user_fun = forms.CharField(
        initial=getattr(
            settings,
            'KELOVE_DATABASE_FIELD_CKFINDER_GET_USER_FUN',
            ''
        ),
        label=_('自定义用户解析方法，须返回 user 对象'),
        help_text=_('留空时，字段从session中获取。示例:django_kelove_database.util.get_user'),
        required=False,
    )

    license_name = forms.CharField(
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_CKFINDER_LICENSE_NAME', ''),
        label=_('License Name'),
        required=False,
    )

    license_key = forms.CharField(
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_CKFINDER_LICENSE_KEY', ''),
        label=_('License Key'),
        required=False,
    )

    connectorPath = forms.CharField(
        initial=getattr(
            settings,
            'KELOVE_DATABASE_FIELD_CKFINDER_CONNECTOR_PATH',
            'django_kelove_database:ckfinder_api'
        ),
        label=_('API 地址'),
        required=False,
    )

    connectorInfo = forms.CharField(
        initial=getattr(
            settings,
            'KELOVE_DATABASE_FIELD_CKFINDER_CONNECTOR_INFO',
            ''
        ),
        label=_('API GET 附加参数'),
        help_text=_('API GET 附加参数 例如： "token=7901a26e4bc422aef54eb45"'),
        required=False,
    )

    skin = forms.ChoiceField(
        widget=RadioSelect,
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_CKFINDER_SKIN', 'neko'),
        choices=(('neko', 'neko'), ('jquery-mobile', 'jquery-mobile'), ('moono', 'moono')),
        label=_('皮肤'),
        required=False,
    )

    swatch = forms.ChoiceField(
        widget=RadioSelect,
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_CKFINDER_SWATCH', 'b'),
        choices=(('a', 'a'), ('b', 'b')),
        label=_('皮肤样式'),
        required=False,
    )

    displayFoldersPanel = forms.BooleanField(
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_CKFINDER_DISPLAY_FOLDERS_PANEL', False),
        label=_('是否显示文件夹面板'),
        required=False,
    )

    @classmethod
    def get_server_settings(cls):
        data = cls.get()
        allowed_fields = ['license_name', 'license_key', 'get_user_fun']
        return {i: data.get(i, None) for i in allowed_fields}

    @classmethod
    def get_client_settings(cls):
        data = cls.get()
        allowed_fields = ['connectorPath', 'connectorInfo', 'skin', 'swatch', 'displayFoldersPanel']
        return {i: data.get(i, None) for i in allowed_fields}


class EditorMdFieldSettings(SettingsForm):
    """
    EditorMd 字段配置
    """

    settings_title: str = _('字段配置 - EditorMd')

    editorTheme = forms.ChoiceField(
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_EDITOR_MD_THEME',
                        KELOVE_DATABASE_FIELD_EDITOR_MD_THEME_DEFAULT),
        required=False,
        label=_('编辑器主题'),
        choices=(
            (i, i) for i in KELOVE_DATABASE_FIELD_EDITOR_MD_THEMES
        )
    )

    previewTheme = forms.ChoiceField(
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_EDITOR_MD_PREVIEW_THEME', 'default'),
        required=False,
        label=_('编辑器预览界面主题'),
        choices=(
            ('default', 'default'),
            ('dark', 'dark'),
        )
    )

    mode = forms.ChoiceField(
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_EDITOR_MD_MODE', KELOVE_DATABASE_FIELD_EDITOR_MD_MODE_DEFAULT),
        required=False,
        label=_('编辑器语言'),
        choices=(
            (i, i) for i in KELOVE_DATABASE_FIELD_EDITOR_MD_MODES
        )
    )

    watch = forms.BooleanField(
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_EDITOR_MD_WATCH', True),
        label=_('是否显示预览窗口'),
        required=False,
    )

    toolbar = forms.BooleanField(
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_EDITOR_MD_TOOLBAR', True),
        label=_('是否显示工具栏'),
        required=False,
    )

    height = forms.IntegerField(
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_EDITOR_MD_HEIGHT', 380),
        label=_('编辑器高度'),
        required=False,
    )

    imageUpload = forms.BooleanField(
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_EDITOR_MD_IMAGE_UPLOAD', True),
        label=_('是否使用文件上传功能'),
        required=False,
    )

    ckfinderUpload = forms.BooleanField(
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_EDITOR_MD_CKFINDER_UPLOAD', True),
        label=_('是否使用ckfinder上传功能'),
        required=False,
    )

    imageUploadURL = forms.CharField(
        initial=getattr(settings, 'KELOVE_DATABASE_FIELD_EDITOR_MD_IMAGE_UPLOAD_URL', ''),
        label=_('文件上传接口URL'),
        required=False,
        help_text=_('使用ckfinder上传功能时，此项无需配置')
    )

    @classmethod
    def get(cls) -> dict:
        data = super().get()
        if data.get('ckfinderUpload', False):
            data['imageUploadURL'] = {}
        return data


class EditorCkFieldSettings(SettingsForm):
    """
    CkEditor 字段配置
    """

    def __init__(self, data=None, files=None, **kwargs):
        super().__init__(data, files, **kwargs)
        self.__toolbar_json_widget()

    settings_title: str = _('字段配置 - EditorCk')

    toolbar = forms.JSONField(
        initial=getattr(
            settings,
            'KELOVE_DATABASE_FIELD_EDITOR_CK_TOOLBAR',
            KELOVE_DATABASE_FIELD_EDITOR_CK_TOOLBAR_DEFAULT
        ),
        required=False,
        label=_('工具栏管理')
    )

    plugins = forms.MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        initial=getattr(
            settings,
            'KELOVE_DATABASE_FIELD_EDITOR_MD_PLUGINS',
            KELOVE_DATABASE_FIELD_EDITOR_CK_PLUGINS
        ),
        required=False,
        label=_('插件管理'),
        choices=(
            (i, i) for i in KELOVE_DATABASE_FIELD_EDITOR_CK_PLUGINS
        )
    )

    def __toolbar_json_widget(self):
        """
        为toolbar字段添加json挂件
        """
        field_name = 'toolbar'
        from .forms.widgets import JSONWidget
        field_settings = {
            "mode": "code",
            "modes": ["code", "tree"],
        }
        json_widget = JSONWidget(attrs={'field_settings': field_settings})
        self.fields[field_name].widget = json_widget
        self.base_fields[field_name].widget = json_widget
