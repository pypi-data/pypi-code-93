# -*- coding: utf-8 -*-
# @Time    : 2020-07-20 14:38
# @Author  : xzr
# @File    : jinja2_env
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

import re

from framework.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.backends.jinja2 import Jinja2
from django.template.library import import_library
from django.urls import reverse
from django.utils.translation import gettext_lazy, ngettext_lazy
from jinja2 import Environment


class TemplateJinja2Backend(Jinja2):
    app_dirname = 'jinja2_templates'


_paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')

filters = []


def environment(**options):
    env = Environment(extensions=['jinja2.ext.i18n'], **options)
    env.install_gettext_callables(gettext=gettext_lazy, ngettext=ngettext_lazy, newstyle=True)

    from django.template.defaultfilters import register as django_default_register
    env.filters.update(django_default_register.filters)

    from .templatetags.mytags import register
    env.filters.update(register.filters)

    for app_name in settings.INSTALLED_APPS:
        try:
            _register = import_library('%s.%s' % (app_name, 'templatetags'))
            env.filters.update(_register.filters)
        except Exception as e:
            pass

    env.globals.update({
            'static'  : staticfiles_storage.url,
            'url'     : reverse,
            'reverse' : reverse,
            'settings': settings
    })
    return env
