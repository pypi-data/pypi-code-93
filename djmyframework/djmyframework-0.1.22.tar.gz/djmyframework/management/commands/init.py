from __future__ import absolute_import

import os
import shutil

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = '初始化框架 复制框架配置文件 config'

    def handle(self, **options):
        from ...scripts.init import init_djframework
        init_djframework()
