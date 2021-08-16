# -*- coding: utf-8 -*-

from framework.translation import _
from django.apps import AppConfig

class {{ camel_case_app_name }}Config(AppConfig):
    name = '{{ app_name }}'
    verbose_name = '{{ app_name }}'