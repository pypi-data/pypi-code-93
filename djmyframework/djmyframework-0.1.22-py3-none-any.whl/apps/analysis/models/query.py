# -*- coding: utf-8 -*-
# 查询类模型
#
import copy
import json
import re
import time
from collections import OrderedDict

from django.db import models

from analysis.apps import AnalysisConfig
from framework.models import BaseModel
from framework.translation import _
from framework.utils import import_func, ObjectDict, trace_msg
from framework.utils.cache import CacheAttribute
from framework.utils.myenum import Enum
from log_def.models import DictDefine, LogDefine


class SqlMarkConfig(ObjectDict):
    mark_name: str
    name: str
    multiple: bool
    single: bool # 是否单选
    fixed: bool  # 是否定值
    template: bool # 模板
    context_func: lambda x: x # 模板上下文
    order_num:int


class SqlMarkManager(object):
    mark_map = OrderedDict({
            # "game_alias"      : {"name"        : "game_alias", "multiple": False,
            #                      'template'    : 'sdk_center/widgets/game_alias_select2.html',
            #                      'context_func': 'sdk_center.views.widgets.get_game_alias_dict'},  # 游戏代号
            # "game_aliass"     : {"name"        : "game_alias", "multiple": True,
            #                      'template'    : 'sdk_center/widgets/game_alias_dialog.html',
            #                      'context_func': 'sdk_center.views.widgets.get_game_alias_dict'},  # 多个游戏代号
            #
            # "server_id"       : {"name"        : "server_id", "multiple": False,
            #                      'template'    : 'game_manage/widgets/group_server_select.html',
            #                      'context_func': 'game_manage.views.widgets.get_group_servers_dict'},  # 服务器ID替换
            # "server_ids"      : {"name"        : "server_id", "multiple": True,
            #                      'template'    : 'game_manage/widgets/group_server_dialog.html',
            #                      'context_func': 'game_manage.views.widgets.get_group_servers_dict'},  # 多个服务器ID替换

            "server_name"     : {"name": "server_name", "multiple": False},  # 服务器名
            "master_id"       : {"name": "master_id", "multiple": False},  # 母服ID
            "master_db"       : {"name": "master_db", "multiple": False},  # 母服db名
            "sdate"           : {"name": "sdate"},  # 开始时间
            "edate"           : {"name": "edate"},  # 结束时间

            # "channel"         : {"name"        : "channel", "multiple": False, 'type': 'str',
            #                      'template'    : 'sdk_center/widgets/agent_channel_alias_select.html',
            #                      'context_func': 'sdk_center.views.widgets.get_agent_channels_dict'},  # 渠道标识
            # "channels"        : {"name"        : "channel", "multiple": True, 'type': 'str',
            #                      'template'    : 'sdk_center/widgets/agent_channel_alias_dialog.html',
            #                      'context_func': 'sdk_center.views.widgets.get_agent_channels_dict'},  # 渠道标识列表

            # "first_channel"   : {"name"        : "channel", "multiple": True, 'type': 'str',
            #                      'template'    : 'sdk_center/widgets/agent_alias.html',
            #                      'context_func': 'sdk_center.views.widgets.get_agent_dict'},  # 渠道标识列表
            # "plan_channel"    : {"name"        : "channel", "multiple": True, 'type': 'str',
            #                      'template'    : 'sdk_center/widgets/plan_agent_channel.html',
            #                      'context_func': 'sdk_center.views.widgets.get_agent_channels_dict'},  # 渠道标识

            "package"         : {"name": "package", "multiple": True, 'type': 'str'},  # 渠道标识
            "media"           : {"name": "media", "multiple": True, 'type': 'str'},  # 媒体账号

            "sdk_code"        : {"name": "sdk_code"},  # 渠道代号

            # "channel_id"      : {"name"        : "channel_id", "multiple": False,
            #                      'template'    : 'game_manage/widgets/agent_channel_select.html',
            #                      'context_func': 'game_manage.views.widgets.get_agent_channels_dict'},  # 渠道id
            # "channel_ids"     : {"name"        : "channel_id", "multiple": True,
            #                      'template'    : 'game_manage/widgets/agent_channel_dialog.html',
            #                      'context_func': 'game_manage.views.widgets.get_agent_channels_dict'},  # 渠道id

            "kouliang_rate"   : {"name": "kouliang_rate"},
            "min_kouliang_num": {"name": "min_kouliang_num"},
            # "game_server_id"  : {"name"    : "game_server_id", "multiple": False,
            #                      'template': 'sdk_center/widgets/game_server_alias.html'},  # 区服ID替换
            # "game_server_ids" : {"name"    : "game_server_id", "multiple": True,
            #                      'template': 'sdk_center/widgets/game_server_alias.html'},  # 多个区服ID替换
            "agent_name"      : {"name": "agent_name"},  # 平台名
            'platform_id'     : {"name": "platform_id", "multiple": False},  # 游戏平台
            'platform_ids'    : {"name": "platform_id", "multiple": True},
            'user_id'         : {"name": "user_id", "multiple": False},  # 管理员id
            'admin_id'        : {"name": "admin_id", "multiple": False},  # 管理员id
            'is_root'         : {"name": "is_root", "multiple": False},  # 是否超级管理员
            'is_manager'      : {"name": "is_manager", "multiple": False}  # 是否管理员
    })

    @classmethod
    def register_mark(cls, sql_mark_config):
        cls.mark_map[sql_mark_config.mark_name] = sql_mark_config


class SqlBuilder(object):
    '''sql
    @param TAG_FORMAT: 默认的标签外围
    @param params:  字典 一键一列表 例如reuqest.POST
    '''
    TAG_FORMAT = '{{%s}}'


    def __init__(self, source_sql, params):
        '''初始化
        @param source_sql 原SQL
        '''
        self.sql = source_sql
        self.query_sql = source_sql.strip()
        self.params = params
        self.order_str = ''
        self.limit_str = ''
        self.mark_map = copy.copy(SqlMarkManager.mark_map)

    def query_sql_handle(self, sql=''):
        '''查询sql转换
        '''
        values_list = []
        for mark_name, config in SqlMarkManager.mark_map.items():
            if self.has_mark(mark_name):  # sql存在这个标签
                param_name = config['name']
                value = self.get_param_value(param_name, config)

                if value or value == 0 or config.get('single', False) or config.get('fixed',
                                                                                    False):  # 先把没值的标记替换,单选和开关可以为空值
                    values_list.append((mark_name, value))
                else:
                    self.empty_param_handle(mark_name)
        if values_list:
            for mark_name, value in values_list:
                self.replace_mark_to_value(mark_name, value)

        return self.query_sql

    def convert_datatable_name(self):

        datatable_tags = re.findall(r'${([^\s,]*)}', self.query_sql)

        if datatable_tags:  # 包含${模型名}标签
            for data_model_name in set(datatable_tags):
                model_class = __import__(data_model_name)
                self.query_sql = self.query_sql.replace('${%s}' % data_model_name, model_class.get_table_name())
        return self.query_sql

    def get_param_value(self, param_name, config):
        '''获取参数值
        '''
        values = self.params.get(param_name, []) or ['']
        the_value = str(values[0])
        if the_value != '':  # 参数不为空
            if not config.get('multiple', False):  # 不是多选
                values = values[0]
            else:
                the_sp = r',|\s'
                if re.search(the_sp, the_value):
                    values = re.split(the_sp, the_value)
            dict_key = config.get('dict', '')  # 输入值转换,支持中文转成id
            if dict_key:
                if not config.get('fixed', False):
                    value_def = DictDefine.get_dict_for_key(dict_key, reverse=True)
                    values = self.convert_input_value(values, value_def, config.get('type'))
                else:  # 固定值
                    values = dict_key
            else:
                values = self.convert_input_value(values, {}, config.get('type'))
        else:
            values = config.get('default_value', '')
        return values

    def convert_input_value(self, values, value_def, type):
        '''转换输入
        '''
        if isinstance(values, (list, tuple, set)):
            _r = []
            for v in values:
                value = str(value_def.get(v, value_def.get(str(v), v)))
                if not value.isdigit() or type == 'str':
                    value = "'%s'" % value
                _r.append(value)
            return ','.join(_r)
        else:
            return value_def.get(values, values)

    def empty_param_handle(self, mark_name, value=' 0=0 '):
        '''传入参数为空时,把 SQL的条件 例如:log_user={{player_id}} 换换成 0=0
        '''
        the_mark = self.make_mark(mark_name)
        # pattern = re.compile(r'''[\w\.`(+=*]*[\W`]?(not[\s]+)?(like|in|=|=>|<=|>|<|!=)[\W]*%s[^\s]*[\s$]*''' % the_mark,flags=re.I)
        pattern = re.compile(r'''[\S]*[\W`]?([\s]+not[\s]+)?(like|in|=|=>|<=|>|<|!=)[\W]*%s[^\s]*[\s$]*''' % the_mark,
                             flags=re.I)
        _s = int(time.time())
        self.query_sql = re.sub(pattern, value, self.query_sql)

    def set_limit(self, page_size, page_num):
        '''设置sql limit
        '''
        page_num, page_size = int(page_num), int(page_size)
        self.limit_str = 'limit %s,%s' % ((page_num - 1) * page_size, page_size)

    def set_order(self, sort_key, sort_type='ASC'):
        if sort_key and sort_type.lower() in ('asc', 'desc'):
            if 'order' in self.query_sql.strip()[-30:].lower():
                self.order_str = ' ,%s %s' % (sort_key, sort_type)
            else:
                self.order_str = ' ORDER BY %s %s' % (sort_key, sort_type)

    def replace_mark_to_value(self, mark_name, value):
        self.query_sql = self.query_sql.replace(self.make_mark(mark_name), str(value))

    def make_mark(self, mark_name):
        return self.TAG_FORMAT % mark_name

    def get_query_sql(self):
        return '%s %s %s' % (Query.filter_sql(self.query_sql), self.order_str, self.limit_str)

    def get_count_sql(self):
        return 'select count(0) from (%s) newTable' % Query.filter_sql(self.query_sql)

    def has_mark(self, mark_name):
        return self.make_mark(mark_name) in self.query_sql

    def generate_mark_conditions(self):
        mark_conditions = {}
        for k, v in self.mark_map.items():
            mark_conditions[k] = v if self.has_mark(k) else False
        return mark_conditions

    def get_context_func(self, mark_name):
        return import_func(self.mark_map[mark_name]['context_func'])


class QueryAnalysis(SqlBuilder):

    def __init__(self, query_model, params):
        self.query = query_model
        self.already_get_query_sql = False
        the_sql = self.query.sql or self.query.get_default_sql()
        super(QueryAnalysis, self).__init__(the_sql, params)
        self.mark_map.update(self.query.field_config)

    def get_tfoot_sql(self):
        '''获取tfoot的汇总sql
        '''
        assert self.already_get_query_sql, '只能先使用get_query_sql 获取查询SQL'
        tmp_sql = self.query_sql
        ftoot_sql = self.query.other_sql
        if ftoot_sql:
            self.query_sql = ftoot_sql
            self.query_sql_handle()
            ftoot_sql = self.query_sql
            self.query_sql = tmp_sql
        return ftoot_sql

    def get_query_sql(self):
        self.already_get_query_sql = True
        if self.query.order and not self.order_str:  # 如果没有排序设置默认查询排序
            self.set_order(self.query.order, self.query.order_type_str)
        return super(QueryAnalysis, self).get_query_sql()

    def get_statistic(self):
        '''获取所需的统计
        '''

        statistic_tags = re.findall(r'<<([^\s,]*)>>', self.query.sql)
        statistic_tags.extend(re.findall(r'<<([^\s,]*)>>', self.query.other_sql))

        result = []
        if statistic_tags:  # 包含<<统计名>>标签
            statistic_names_d = DictDefine.get_dict_for_key('statistic_name', reverse=True)
            for s_name in set(statistic_tags):
                s_id = statistic_names_d.get(re.sub(r'\s', '', s_name))  # 去除空格等特殊字符
                if s_id:
                    result.append((s_id, s_name))

        return result

    def query_sql_handle(self):
        '''query_sql_handle 增加获取统计id 使用方法 <<统计名>>
        '''
        record = super(QueryAnalysis, self).query_sql_handle()
        if isinstance(self.query_sql, bytes):
            self.query_sql = self.query_sql.decode('utf8')
        statistic_tags = re.findall(r'<<([^\s,]*)>>', self.query_sql)
        from .statistic import Statistic
        if statistic_tags:  # 包含<<统计名>>标签
            statistic_names_d = dict(Statistic.objects.values_list('name',
                                                                   'id'))  # ,DictDefine.get_dict_for_key('statistic_name', reverse=True)
            for s_name in set(statistic_tags):
                s_id = statistic_names_d.get(re.sub(r'\s', '', s_name))  # 去除空格等特殊字符
                if s_id:
                    self.query_sql = self.query_sql.replace('<<%s>>' % s_name, '"%s"' % s_id)
        # 限制使用的统计
        if self.has_mark("statistic"):
            statistic_list = self.get_statistic()
            self.replace_mark_to_value("statistic", ",".join([s_id for s_id, _ in statistic_list]))

        return self.query_sql

    def has_mark(self, mark_name):
        return super(QueryAnalysis, self).has_mark(mark_name)

    def has_conditions(self):
        for k, v in self.query.field_config.items():
            if v.get('search', ''):
                return True


class Query(BaseModel):
    """查询
    """
    log_key = models.CharField('关联表标识', max_length=30, db_index=True, null=False)
    log_type = models.IntegerField(default=0)

    class OrderType(Enum):
        DESC = 1, _('倒序')
        AESC = 0, _('正序')

    key = models.CharField('查询标识', default='', max_length=100, null=False, blank=True, db_index=True)
    name = models.CharField('查询名称', default='', max_length=100, null=False, blank=False, unique=True)
    select = models.CharField(_('查询字段'), max_length=1000, null=False, blank=True)
    where = models.CharField(max_length=500, null=False, blank=True)
    group = models.CharField('用途分组', max_length=50, null=False, blank=True, default='')
    order = models.CharField(max_length=20, null=False, blank=True, default='')
    order_type = models.IntegerField(default=OrderType.AESC, choices=OrderType.member_list(), null=False)
    sql = models.TextField(_('SQL'), default='', null=False, blank=True)
    other_sql = models.TextField(_('其他SQL'), default='', null=False, blank=True)
    cache_validate = models.IntegerField(default=0, null=True)

    remark = models.CharField('备注', max_length=1000, blank=True)
    _field_config = models.TextField('查询字段定义', default="", blank=True)
    template_name = models.CharField('模版名', max_length=32, blank=True)

    _DEFAULT_FIELD_CONFIG = {
            "标记名": {"name"  : "参数名", "dict": "", "sort": False, "order_num": 99, "multiple": False,
                    "search": False, "merge_value": True}}

    __cache_config = None

    class Meta:
        app_label = AnalysisConfig.name
        ordering = ('id',)

    @CacheAttribute
    def log_def_list(self):
        return LogDefine.objects.using('read').all()

    def save(self, *args, **kwargs):
        super(Query, self).save(*args, **kwargs)

    def get_default_sql(self):
        ''' 默认SQL
        '''
        log_def = self.log_def
        the_sql = '''SELECT %s FROM %s WHERE log_time  BETWEEN '{{sdate}}' AND '{{edate}}' ''' % (
                self.select, log_def.table_name)
        if self.where:
            the_sql += ' AND %s' % self.where
        if self.order:
            the_sql += ' ORDER BY %s %s' % (self.order, self.order_type_str)

        for field_name, config in log_def.config.items():
            verbose_name = config['verbose_name']
            if verbose_name:
                the_sql = the_sql.replace(verbose_name, field_name)
        return the_sql

    @property
    def order_type_str(self):
        return 'DESC' if self.order_type == 1 else 'AESC'

    @CacheAttribute
    def log_def(self):
        return LogDefine.objects.filter(key=self.log_key).first()

    @property
    def is_center_query(self):
        '''是否中央查询
        '''
        try:
            return self.log_def.status == LogDefine.PositionType.CENTER
        except:
            return True

    @CacheAttribute
    def selects(self):
        return [f.strip() for f in self.select.split(',') if f]

    @property
    def field_config(self):
        '''字段定义
        '''
        try:
            s_d = OrderedDict()
            self.__cache_config = self.__cache_config or OrderedDict(
                    sorted(json.loads(self._field_config).items(), key=lambda x: x[1]['order_num']))
        except:

            print(trace_msg())
            self.__cache_config = self._DEFAULT_FIELD_CONFIG

        return self.__cache_config

    @field_config.setter
    def field_config(self, obj_value):
        if isinstance(obj_value, dict):
            obj_value = json.dumps(obj_value, ensure_ascii=False)
        self._field_config = obj_value

    @classmethod
    def filter_sql(cls, sql):
        p = re.compile('(update|delete|modify|lock[\s]+|drop|table)', re.I)
        sql = p.sub('', sql)
        return sql

    @CacheAttribute
    def safe_sql(self):
        return self.__class__.filter_sql(self.sql)

    def __unicode__(self):
        return '%s' % self.name


filter_sql = Query.filter_sql
