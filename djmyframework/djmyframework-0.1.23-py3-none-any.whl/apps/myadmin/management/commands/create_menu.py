# coding=utf-8

import importlib

from django.core.management.base import BaseCommand

from myadmin.models.menu import MenuConfig


class Command(BaseCommand):
    help = '创建默认菜单,可以指定 menu.py 文件创建'

    def add_arguments(self, parser):
        self.parser = parser
        super(Command, self).add_arguments(parser)

        parser.add_argument(
                "--auto", "-a", action="store_true", dest="auto",
                help="是否自动根据 app route 自动创建"
        )
        parser.add_argument(
                "--force", "-f", action="store_true", dest="force",
                help="是否强制更新 菜单权限 "
        )
        parser.add_argument(
                "--menu", "-m", dest="menu", default='',
                help="指定 MenuList"
        )
        parser.add_argument(
                "--clear", "-clr", dest="clear", action="store_true",default=False,
                help="清除所有 菜单"
        )
        parser.add_argument('app_name', nargs='*')

    def handle(self, *args, **options):
        menu_config_list = None
        # self.parser.print_help()
        app_names = options.get('app_name', [])
        print(len(app_names), app_names)
        if options['auto']:
            app_name_list = app_names
            menu_config_list = MenuConfig.get_install_app_menu_config_list(app_name_list)
            MenuConfig.create_menu_from_config(menu_config_list, options['force'])
        elif options['menu']:
            module_str = options['menu'].strip('.py')
            module = importlib.import_module(module_str, 'config')
            menu_config_list = module.MenuList
            MenuConfig.create_menu_from_config(menu_config_list, options['force'])
