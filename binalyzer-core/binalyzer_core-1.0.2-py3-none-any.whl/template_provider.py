# -*- coding: utf-8 -*-
"""
    binalyzer_core.template_provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements basic template providers.

    :copyright: 2021 Denis Vasilík
    :license: MIT
"""


class TemplateProviderBase(object):
    @property
    def template(self):
        pass

    @template.setter
    def template(self, value):
        pass


class TemplateProvider(TemplateProviderBase):
    def __init__(self, template):
        self._template = template

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        self._template = value


class PlainTemplateProvider(TemplateProvider):
    def __init__(self, template=None):
        from .template import Template

        if template is None:
            template = Template()
        super(PlainTemplateProvider, self).__init__(template)
