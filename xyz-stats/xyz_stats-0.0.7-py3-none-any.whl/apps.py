# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class Config(AppConfig):
    name = 'xyz_stats'
    label = 'stats'
    verbose_name = '统计'

    def ready(self):
        super(Config, self).ready()
        # from . import receivers