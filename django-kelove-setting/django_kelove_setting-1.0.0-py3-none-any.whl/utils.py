"""
utils.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/29/21 10:46 AM
"""

from . import load_object
from .setting_forms import Settings as SettingsForm


def get_settings_form_class(form_class):
    """
    根据表单标识获取表单配置类
    :param form_class:
    :return:
    """

    if isinstance(form_class, str):
        try:
            form = load_object(form_class)
        except (ModuleNotFoundError, AttributeError):
            form = None
    else:
        form = form_class

    if not issubclass(form, SettingsForm):
        form = None
    return form
