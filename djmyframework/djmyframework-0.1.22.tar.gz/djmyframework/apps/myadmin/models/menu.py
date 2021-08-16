# -*- coding: utf-8 -*-
# @Time    : 2019-09-03 11:49
# @Author  : xzr
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 系统 :管理员,权限,角色相关模型

from __future__ import absolute_import
import functools
import logging
import re
import urllib

from django.apps import apps
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.management.commands.show_urls import Command, simplify_regex

from framework.enums import BoolEnum
from framework.models import BaseModel
from framework.utils import ObjectDict
from framework.utils.single_process import SingleProcessDeco
from ..apps import MyadminConfig
_logger = logging.getLogger(__file__)


class Menu(BaseModel):
    """
        菜单模型
    """

    parent_id = models.IntegerField(_('父节点id'), default=0)
    alias = models.CharField(_('显示名'), max_length=100, db_index=True)
    name = models.CharField(_('权限名'), max_length=128, blank=True, db_index=True, validators=
    [RegexValidator(r'^[a-zA-Z][0-9A-Za-z_]+$', _('开头非数字,数字加字母组合'))])
    url = models.CharField(_('访问地址带参数'), max_length=400, blank=True, default='')
    url_path = models.CharField(_('访问路径'), max_length=128, null=True, db_index=True)

    icon = models.CharField(_('图标'), max_length=100, null=True, blank=True, default='')
    css = models.CharField(_("样式"), max_length=100, null=True, blank=True, default='')
    order = models.IntegerField(_('排序'), default=0)
    is_show = models.IntegerField(_('显示'), default=BoolEnum.Yes, db_index=True, choices=BoolEnum.member_list())
    is_log = models.IntegerField(_('记录日志'), default=BoolEnum.No, choices=BoolEnum.member_list())

    class Meta:
        app_label = MyadminConfig.name
        ordering = ['parent_id', 'order']

    @classmethod
    def generate_name(self, url):
        name = url.replace('/', '_').strip('_')
        return name

    def save(self, *args, **kwargs):
        self.url_path = self.url.split('?', 1)[0]
        if not self.name:
            self.name = Menu.generate_name(self.url_path)

        return super(Menu, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s' % self.alias

    @property
    def label(self):
        return _(self.alias)

    @classmethod
    def url_decode(cls, url_params):
        '''URL参数返回一个字典
        '''
        params = {}
        for o in url_params.split('&'):
            if '=' in o:
                kv = o.split('=')
                if len(kv) != 2:
                    continue
                k, v = kv
                params[k] = urllib.parse.unquote_plus(v)
        return params

    def get_url_params(self):
        '''返回url的参数字典
        '''
        url_params = self.url.split('?', 2)
        if len(url_params) == 2:
            return Menu.url_decode(url_params[1])
        return {}

    def is_match_url_parmas(self, menu_parmas):
        return self._is_dict_issubset(self.get_url_params(), menu_parmas)

    def _is_dict_issubset(self, dict1, dict2):
        set1 = set(dict1.items())
        set2 = set(dict2.items())
        return set1.issubset(set2)


class MenuConfig(ObjectDict):

    def __init__(self, von='', menu_alias='', url='', is_log=0, is_show=1, name='', app_name='', *args, **kwargs):
        self.von = str(von)
        self.parent_id = '0' if self.von.count('.') == 0 else self.von.split('.', 2)[0]
        self.alias = menu_alias
        self.url = url.strip()
        self.is_log = is_log
        self.is_show = is_show
        self.name = name
        self.app_name = app_name

    @staticmethod
    def find_view_func_doc(func, method_name):
        _func = func
        return _func.__doc__.strip().split('\n')[0][:20] if _func.__doc__ else ''

    @classmethod
    def autodiscover_app_view_functions(cls):
        from framework.views import is_notcheck
        urlconf = __import__(getattr(settings, 'ROOT_URLCONF'), {}, {}, [''])
        app_menu_map = {}
        views = []
        decorator = ['login_required']

        view_functions = Command().extract_views_from_urlpatterns(urlconf.urlpatterns)
        for (func, regex, url_name) in view_functions:
            if hasattr(func, '__globals__'):
                func_globals = func.__globals__
            elif hasattr(func, 'func_globals'):
                func_globals = func.func_globals
            else:
                func_globals = {}

            decorators = [d for d in decorator if d in func_globals]

            if isinstance(func, functools.partial):
                func = func.func
                decorators.insert(0, 'functools.partial')

            if hasattr(func, '__name__'):
                func_name = func.__name__
            elif hasattr(func, '__class__'):
                func_name = '%s()' % func.__class__.__name__
            else:
                func_name = re.sub(r' at 0x[0-9a-f]+', '', repr(func))

            module = '{0}.{1}'.format(func.__module__, func_name)
            url_name = url_name or module
            url = simplify_regex(regex).replace('[/]', '')
            decorator = ', '.join(decorators)

            if url_name.count('.') >= 1:

                url_name_split = url_name.split('.')
                method_name = url_name_split[-1]
                if hasattr(func, 'actions'):
                    func = getattr(func.cls, method_name, None)
                if is_notcheck(func):
                    _logger.info('%s is notcheck' % func)
                    continue
                views_data = ObjectDict()
                views_data.url_name = url_name
                views_data.method_name = method_name
                views_data.app_name = module.split('.')[0]
                views_data.url = url
                views_data.module = module

                views_data.describe = MenuConfig.find_view_func_doc(func, views_data.method_name)
                views_data.module_name = module
                app_menu_map.setdefault(views_data.app_name, {})
                app_menu_map[views_data.app_name].setdefault(views_data.module_name, [])
                app_menu_map[views_data.app_name][views_data.module_name].append(views_data)
            else:
                a = 3

        return app_menu_map

    @classmethod
    def get_install_app_menu_config_list(cls, app_name_list=None):

        menu_config_list = []

        if not isinstance(app_name_list, (list, tuple)) and app_name_list is not None:
            app_name_list = [app_name_list]
        print(app_name_list)
        for app_i, (app_name, module_views_data_map) in enumerate(cls.autodiscover_app_view_functions().items()):

            if app_name_list:
                if app_name not in app_name_list:
                    continue
            app_alias = apps.get_app_config(app_name).verbose_name or app_name
            app_root_menu_config = MenuConfig()
            app_root_menu_config.von = str(app_i + 1)
            app_root_menu_config.alias = app_alias
            app_root_menu_config.name = app_name
            app_root_menu_config.app_name = app_name
            app_root_menu_config.app_alias = app_alias
            app_root_menu_config.is_show = True
            app_root_menu_config.is_log = False
            menu_config_list.append(app_root_menu_config)

            for module_i, (module_name, views_datas) in enumerate(module_views_data_map.items()):
                module_i += 1
                for view_i, views_data in enumerate(views_datas):

                    von_list = [app_root_menu_config.von]
                    von_list.append(str(module_i))
                    if not view_i == 0:
                        von_list.append(str(view_i))
                    module_menu_config = MenuConfig()
                    module_menu_config.von = '.'.join(von_list)

                    module_menu_config.alias = views_data.describe or views_data.url_name
                    # module_menu_config.name = views_data.url_name.replace('.', '_')
                    module_menu_config.name = views_data.url.replace('/', '_').strip('_')
                    module_menu_config.app_name = app_name
                    module_menu_config.app_alias = app_alias
                    module_menu_config.url = views_data.url
                    module_menu_config.is_show = views_data.method_name == 'list'
                    module_menu_config.is_log = True
                    menu_config_list.append(module_menu_config)
        return menu_config_list

    fixId = 0
    Menu_Map = {}
    Menu_model_map = {}

    @classmethod
    @SingleProcessDeco()
    def create_menu_from_config(cls, menu_config_list=None, force=False, add_menus=None):

        menu_config_list = menu_config_list
        for mc in menu_config_list:
            try:

                alias = mc.alias
                if not alias or not mc.von:
                    continue

                url = mc.url
                # name = Menu.generate_name(url,alias)
                if mc.name:
                    name = mc.name
                else:
                    name = mc.alias

                cls.Menu_Map[mc.von] = name

                menu_model = Menu.objects.filter(name=name).first()
                is_exists = menu_model is not None
                menu_model = menu_model or Menu()
                if is_exists:
                    print('%s,%s is  is_exists' % (menu_model.name, menu_model.alias))

                parentId, order = cls.get_mc_parent(mc)  # 处理获得id，父id，排序

                if add_menus is not None:
                    allow_save = not is_exists and mc.name in add_menus
                else:
                    allow_save = not is_exists or force
                if allow_save:
                    menu_model.alias = alias if force else (menu_model.alias or alias)
                    menu_model.name = mc.name
                    menu_model.parent_id = parentId
                    menu_model.url = url
                    menu_model.css = ''
                    if parentId != 0:
                        if not menu_model.icon and not url and not menu_model.css and mc.is_show:
                            menu_model.css = menu_model.css or ''
                        # parent_model = cls.Menu_model_map.get(menu_model.parent_id, None)
                        menu_model.url = url
                    menu_model.is_show = mc.is_show
                    menu_model.is_log = mc.is_log
                    menu_model.order = order
                    menu_model.save()
                    print('%s, %s %s 菜单添加完成.' % (menu_model.name, mc.von, menu_model.alias))
                cls.Menu_model_map[name] = menu_model
                # print('%s %s [%s] %s done !' % (menu.alias , menu.name,url, menu.css))
            except Exception:
                print('-' * 40)
                print(mc.von, mc.alias, mc.name)
                raise Exception

    @classmethod
    def get_mc_parent(cls, mc):
        von = mc.von
        parentId = '0'
        if not '.' in von:
            cls.fixId += 1
            order = cls.fixId
        else:
            von_split = von.split('.')
            parent_von = '.'.join(von_split[:-1])
            order = von_split[-1]
            parent_name = cls.Menu_Map.get(parent_von)

            parent_menu_model = cls.Menu_model_map.get(parent_name,
                                                       Menu.objects.filter(name=parent_name).only('id').first())
            if parent_menu_model:
                parentId = parent_menu_model.id or parentId

        return parentId, order


class UserDefinedMenu(BaseModel):
    ''' 用户自定义菜单模型 '''
    user_id = models.IntegerField(_('所属管理员ID'))
    defined_menu = models.TextField(_("用户定义的菜单项"), max_length=1000)
    map_menu = models.TextField(_("系统菜单的映射"), max_length=1000)
    update_time = models.DateTimeField()

    def __unicode__(self):
        return self.id

    class Meta:
        pass
