# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO


class Command(BaseCommand):

    help = '同步 账号到 svn 文件'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        from svn_admin.models import SvnPath
        SvnPath.sync_svn_config_file()
