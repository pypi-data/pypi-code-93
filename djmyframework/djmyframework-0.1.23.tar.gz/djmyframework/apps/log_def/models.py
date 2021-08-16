# -*- coding: utf-8 -*-
# 日志类模型
#

from django.db import connections, models
from django.db.models import fields

from framework.models import BaseModel, JSONField, SqlModelMixin
from framework.translation import _
from framework.validators import LetterValidator
from framework.utils import datetime_to_str, json_dumps
from framework.utils.cache import CacheAttribute
from framework.utils.myenum import Enum

try:
    import cPickle as pickle
except ImportError:
    import pickle
import json
from framework.settings import settings
import traceback
import os


class BigIntegerAutoField(fields.BigIntegerField):
    def db_type(self, connection):
        if 'mysql' in connection.__class__.__module__:
            return 'bigint AUTO_INCREMENT'
        return super(BigIntegerAutoField, self).db_type(connection)


class BaseLog(models.Model, SqlModelMixin):
    '''日志基本模型
    '含有空值的列很难进行查询优化，因为它们使得索引、索引的统计信息以及比较运算更加复杂。你应该用0、一个特殊的值或者一个空串代替空值。

    '''
    # https://blog.jcole.us/2013/05/02/how-does-innodb-behave-without-a-primary-key/

    id = models.BigAutoField(primary_key=True)

    def __unicode__(self):
        return '%d_%d_%s'(self.log_type, self.log_user, self.log_time.strftime('%Y-%m-%d'))

    def log_time_str(self):
        return datetime_to_str(self.log_time)

    def get_table_name(cls):
        return cls._Meta.db_table

    @classmethod
    def get_create_table_sql(cls, table_name):
        sql = 'CREATE TABLE IF NOT EXISTS  %s LIKE %s;' % (table_name, cls._Meta.db_table)
        return sql

    class _Meta:  # 防止使用log表时失去元表名
        abstract = True
        db_table = u'log_0_new'

    Meta = _Meta


Log = BaseLog


class LogDefineMixin(object):
    class FieldType(Enum):
        pass

    @classmethod
    def get_truncate_table_sqls(cls):
        sqls = []
        log_defs = cls.objects.filter(status=cls.Status.NORMAL)
        for ld in log_defs:
            if ld.key == 'statistic_date':
                continue
            sqls.append('truncate table %s;' % ld.table_name)
        return sqls

    def get_create_table_sql(self):
        return self.LogModel.get_create_table_sql(self.table_name)

    def get_create_index_sqls(self, default_index=True):
        sqls = []
        for f in self.get_index_fields(default_index):
            index_name = '%s_%s_index' % (self.table_name, f['filed_name'])
            sql = "CREATE INDEX `%s` ON `%s` (%s);" % (index_name, self.table_name, f['filed_name'])
            sqls.append(sql)
        return sqls

    def get_default_config(self):
        '''默认的日志类配置
        '''
        _d = {}
        for f in self.LogModel._meta.fields:
            if f.name.lower() == 'id':
                continue

            _d[f.name] = {"default_db_index": f.db_index, "verbose_name": f.verbose_name, 'type': ''}
        return _d

    def get_index_fields(self, default_index=True):
        index_fields = []
        default_config = self.get_default_config()
        for k, v in self.config.items():
            if v.get('db_index', '') and v.get('verbose_name', '').strip():
                v['filed_name'] = k
                # 默认索引选择创建
                if v.get('default_db_index') and not default_index:
                    continue
                index_fields.append(v)
        return index_fields

    @classmethod
    def get_create_table_sqls(cls, is_center=False):
        '''获取需要创建表的sql
        '''
        status = cls.Status.CENTER if is_center else cls.Status.NORMAL
        sqls = []
        for t in cls.objects.filter(status=status):
            sqls.append(t.get_create_table_sql())
        return sqls

    def get_field_name_by_verbose_name(self, verbose_name):
        for field_name, config in self.config:
            if verbose_name == config['verbose_name']:
                return field_name


class LogDefine(BaseModel, LogDefineMixin):
    '''日志类定义
    '''

    LogModel = Log

    class PositionType(Enum):
        SERVER = 0, _('分服')
        CENTER = 1, _('中央服')
        KUAFU = 2, _('跨服')

    Status = PositionType

    name = models.CharField(_('日志名'), max_length=50)
    key = models.CharField(_('日志表标识'), max_length=100, db_index=True, validators=[LetterValidator])
    remark = models.CharField(_('备注'), max_length=1000)
    status = models.IntegerField(_('保存位置'), default=0, choices=PositionType.member_list())
    _config = models.TextField(_('配置'))
    trigger = models.TextField(_('触发器sql'), default="", null=False, blank=True)

    #  todo 这里未来兼容sql文件导入和mysqldb执行的sql 处理有点乱, 到时再改
    def get_other_sqls(self, is_sql_file=False):
        '''获取其他sql
        @is_sql_file:是否sql文件用的
        '''
        sqls = []
        sp = ';'
        the_cut_sp = '\\'
        if '//' in self.trigger:
            sp = '//'
        for sql in self.trigger.split(sp):
            if the_cut_sp in sql:
                if is_sql_file:
                    sql = sql.replace(the_cut_sp, '')
                else:
                    sql = ''
            elif not is_sql_file:
                sql = sql.replace('$$', '')
            if sql:
                sqls.append('%s' % sql)
        return sqls

    @property
    def config(self):
        _r = {}
        field_config = self.get_default_config()
        try:
            _r = json.loads(self._config)
            for k in sorted(_r.keys(), reverse=True):
                field_config[k].update(_r.get(k, {}))
        except:
            pass
        _r = field_config

        return _r

    @config.setter
    def config(self, obj_value):
        if isinstance(obj_value, dict):
            obj_value = json.dumps(obj_value)
        self._config = obj_value

    @CacheAttribute
    def json_config(self):

        return json_dumps(self.config)

    @property
    def table_name(self):
        return 'log_%s' % self.key.strip()

    def save(self, *args, **kwargs):
        return super(LogDefine, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s' % self.key

    class Meta:
        pass


class DictBaseType(object):
    '''基本字典类型
    '''
    NAME = '字典'
    DEFAULT_JSON = '{}'

    def __init__(self, dict_config):
        self.dict = dict_config

    def get_dict(self):
        return self.dict


class DBDictType(DictBaseType):
    '''数据表
    '''
    NAME = '数据表'
    DEFAULT_JSON = '{"table_name":"","key_name":"","value_name":""}'

    def get_dict(self):
        _r = {}
        sql = 'SELECT DISTINCT `{key_name}` a,`{value_name}` b FROM {table_name} LIMIT 10000;'
        sql = sql.format(**self.dict)
        cur = connections['read'].cursor()
        cur.execute(sql)
        for row in cur.fetchall():
            _r[str(row[0])] = row[1]
        return _r


ROOT_PATH = settings.BASE_DIR


class FileDicType(DictBaseType):
    '''从文件内拿json
    '''
    NAME = '文件'
    DEFAULT_JSON = '{"file_path":"","key_name":"","value_name":""}'

    def get_dict(self):
        _r = {}
        the_file_path = os.path.join(ROOT_PATH, self.dict['file_path'])
        try:
            with open(the_file_path, 'rb') as fp:
                _r = the_dict_data = json.loads(fp.read())
        except:
            pass
        return _r


from framework.utils import get_files_from_dir


class DirDictType(DictBaseType):
    '''目录里拿字典
    '''
    NAME = '目录'
    DEFAULT_JSON = '{"dir_path":"","key_name":"","value_name":""}'

    def get_dict(self):
        _r = {}
        the_dir_path = os.path.join(ROOT_PATH, self.dict['dir_path'])

        try:
            if os.path.isdir(the_dir_path):
                for the_json_file in get_files_from_dir(the_dir_path, '.json'):

                    with open(the_json_file, 'rb') as fp:
                        json_str = fp.read()
                        json_data = json.loads(json_str)
                        key_name = self.dict.get('key_name', '')
                        value_name = self.dict.get('value_name', '')
                        if key_name and value_name:
                            key = json_data.get(key_name, '')
                            value = json_data.get(value_name, '')
                            if key:
                                _r[key] = value
        except:
            print(the_dir_path)
            traceback.print_exc()
        return _r


class DictDefine(BaseModel):
    '''字典定义
    '''
    TYPE_DICT = {0: DictBaseType,
                 1: DBDictType,
                 2: FileDicType,
                 3: DirDictType
                 }

    SELECT_CHOICES = [(k, v.NAME, v.DEFAULT_JSON) for k, v in TYPE_DICT.items()]
    _TYPE_CHOICES = ((k, v.NAME) for k, v in TYPE_DICT.items())

    name = models.CharField('字典名', max_length=100, blank=False)
    key = models.CharField('标识名', max_length=50, unique=True, db_index=True, validators=[LetterValidator])
    json_dict = JSONField('存键值', default='{}', null=False, blank=True)
    group = models.CharField('组', max_length=50, default="")
    type = models.IntegerField('字典的类型', default=0, choices=_TYPE_CHOICES)
    remark = models.CharField('备注', max_length=400)

    __cache_dict = {}

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        pass

    @property
    def dict(self):
        try:
            _d = json.loads(self.json_dict)
        except:
            _d = {}
        return _d

    @dict.setter
    def dict(self, obj_value):
        # for k, v in obj_value.items():
        #    obj_value[k] = v.encode('utf-8')
        _data = json.dumps(obj_value)
        self.json_dict = _data

    @classmethod
    def get_dict_for_key(cls, key_name, reverse=False):
        _r = {}
        try:
            if '{' in key_name:
                _r = json.loads(key_name)
            else:
                dict_model = cls.objects.get(key=key_name)
                _r = dict_model.get_dict()
            if reverse:
                _r = cls.reverse_dict(_r)
        except:
            pass
        return _r

    @staticmethod
    def reverse_dict(_dict):
        '''反转字典
        '''
        return dict((v, k) for k, v in _dict.items())

    def get_dict(self):
        '''获取字典
        '''
        _r = {}
        if self.__cache_dict: return self.__cache_dict
        type_class = self.TYPE_DICT.get(self.type)
        try:
            dict_handler_obj = type_class(self.dict)
            _r = dict_handler_obj.get_dict()
        except:
            traceback.print_exc()
        self.__cache_dict = _r
        return self.__cache_dict

    def get_json_data(self):
        return self.json_dict

    @classmethod
    def get_group(cls):
        '''获取字典的分组
        '''
        groups = [g for g in cls.objects.using('read').values_list('group', flat=True).distinct() if g]
        return groups
