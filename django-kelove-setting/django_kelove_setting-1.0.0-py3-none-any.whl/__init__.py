"""
__init__.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/24/21 11:10 AM
"""

from importlib import import_module

default_app_config = "django_kelove_setting.apps.DjangoKeloveSettingConfig"

# 配置注册属性名
KELOVE_SETTINGS_APP_KEY = 'kelove_settings'


def load_object(path: str):
    """
    Load an object given its absolute object path, and return it.
    object can be a class, function, variable or an instance.
    path ie: 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware'
    """

    dot = path.rindex('.')
    module, name = path[:dot], path[dot + 1:]
    mod = import_module(module)
    return getattr(mod, name)
