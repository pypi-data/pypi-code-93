# coding=utf-8

import configparser
import json
import os
import sys

from django.core.management import BaseCommand

from framework.utils import OrderedDict
from ...models import LogDefine


class Command(BaseCommand):
    '''按 base_table.ini创建基本日志类定义
    '''

    def add_arguments(self, parser):

        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        print(args)
        if len(args) == 0:
            sys.stdout.write('缺少参数: 请输入菜需要创建的菜单数据文件.')
            return
        else:
            ini_file = args[0]
            if not os.path.isfile(ini_file):
                sys.stdout.write('错误: 无效的文件路径.')
                return
            config = configparser.ConfigParser(dict_type=OrderedDict)

            config.read(ini_file)

            for section in config.sections():
                opt = dict(config.items(section))
                log_def, created = LogDefine.objects.get_or_create(key=section)
                log_def.key = section.strip()
                log_def.name = opt.get('name')
                log_def.remark = opt.get('remark', '')
                log_def.status = LogDefine.Status.CENTER if opt.get('center', '') else LogDefine.Status.SERVER
                field_config = opt.get("config")
                try:
                    log_def.config = json.loads(field_config)
                except:
                    pass
                log_def.save()
                print('create log_def: %s %s is_center:%s ' % (log_def.key,
                                                               log_def.name,
                                                               log_def.status
                                                               ))
                if log_def.status == LogDefine.Status.CENTER:
                    from django.db import connection
                    create_table_sql = LogDefine.LogModel.get_create_table_sql('log_%s' % log_def.key)
                    print(create_table_sql)
                    conn = connection
                    cur = conn.cursor()

                    cur.execute(create_table_sql)
