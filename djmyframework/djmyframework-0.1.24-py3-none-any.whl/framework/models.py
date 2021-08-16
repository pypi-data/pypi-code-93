# -*- coding: utf-8 -*-
import datetime
import hashlib
import json
import re
from collections import OrderedDict

import timezone_field
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.color import no_style
from django.core.validators import RegexValidator
from django.db import close_old_connections, connection, models
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import DictField, CharField

from .utils import json_dumps, ObjectDict, trace_msg
from .utils.cache import CachedClassAttribute
from .utils.log import logger
from .validators import LetterValidator


def truncate_name(name, length=None, hash_len=4):
    """Shortens a string to a repeatable mangled version with the given length.
    """
    if length is None or len(name) <= length:
        return name

    hsh = hashlib.md5(force_bytes(name)).hexdigest()[:hash_len]
    return '%s%s' % (name[:length - hash_len], hsh)


def close_connections():
    try:
        close_old_connections()
    except Exception as e:
        logger.error(e)


class SqlModel(object):
    connection = connection

    @classmethod
    def sql_for_inline_foreign_key_references(cls, model, field, known_models, style):
        """
        Return the SQL snippet defining the foreign key reference for a field.
        """
        qn = cls.connection.ops.quote_name
        rel_to = field.rel.to
        if rel_to in known_models or rel_to == model:
            output = [style.SQL_KEYWORD('REFERENCES') + ' ' +
                      style.SQL_TABLE(qn(rel_to._meta.db_table)) + ' (' +
                      style.SQL_FIELD(qn(rel_to._meta.get_field(
                              field.rel.field_name).column)) + ')' +
                      cls.connection.ops.deferrable_sql()
                      ]
            pending = False
        else:
            # We haven't yet created the table to which this field
            # is related, so save it for later.
            output = []
            pending = True

        return output, pending

    @classmethod
    def sql_create_model(cls, model, style=None, known_models=[]):
        """
        Returns the SQL required to create a single model, as a tuple of:
            (list_of_sql, pending_references_dict)
        """
        style = style or no_style()
        opts = model._meta
        if not opts.managed or opts.proxy or opts.swapped:
            return [], {}
        final_output = []
        table_output = []
        pending_references = {}
        qn = cls.connection.ops.quote_name
        for f in opts.local_fields:
            col_type = f.db_type(connection=cls.connection)
            col_type_suffix = cls.connection.data_types_suffix.get(f.get_internal_type())
            if col_type_suffix:
                col_type += " %s" % col_type_suffix

            tablespace = f.db_tablespace or opts.db_tablespace
            if col_type is None:
                # Skip ManyToManyFields, because they're not represented as
                # database columns in this table.
                continue
            # Make the definition (e.g. 'foo VARCHAR(30)') for this field.
            field_output = [style.SQL_FIELD(qn(f.column)),
                            style.SQL_COLTYPE(col_type)]
            # Oracle treats the empty string ('') as null, so coerce the null
            # option whenever '' is a possible value.
            null = f.null
            if (f.empty_strings_allowed and not f.primary_key and
                    cls.connection.features.interprets_empty_strings_as_nulls):
                null = True
            if not null:
                field_output.append(style.SQL_KEYWORD('NOT NULL'))
            if f.primary_key:
                field_output.append(style.SQL_KEYWORD('PRIMARY KEY'))
            elif f.unique:
                field_output.append(style.SQL_KEYWORD('UNIQUE'))

            if f.has_default():
                default = f.get_default()
                if default in [False, True]:
                    default = str(int(f.get_default()))
                elif isinstance(default, str):
                    default = "'%s'" % default
                else:
                    default = qn(default)
                field_output.append(style.SQL_KEYWORD('DEFAULT') + ' ' + default)

            if tablespace and f.unique:
                # We must specify the index tablespace inline, because we
                # won't be generating a CREATE INDEX statement for this field.
                tablespace_sql = connection.ops.tablespace_sql(
                        tablespace, inline=True)
                if tablespace_sql:
                    field_output.append(tablespace_sql)
            if getattr(f, 'rel', None) and getattr(f, 'db_constraint', None):
                ref_output, pending = cls.sql_for_inline_foreign_key_references(
                        model, f, known_models, style)
                if pending:
                    pending_references.setdefault(f.rel.to, []).append(
                            (model, f))
                else:
                    field_output.extend(ref_output)
            table_output.append(' '.join(field_output))
        for field_constraints in opts.unique_together:
            table_output.append(style.SQL_KEYWORD('UNIQUE') + ' (%s)' %
                                ", ".join(
                                        [style.SQL_FIELD(qn(opts.get_field(f).column))
                                         for f in field_constraints]))

        full_statement = [style.SQL_KEYWORD('CREATE TABLE') + ' ' +
                          style.SQL_TABLE(qn(opts.db_table)) + ' (']
        for i, line in enumerate(table_output):  # Combine and add commas.
            full_statement.append(
                    '    %s%s' % (line, ',' if i < len(table_output) - 1 else ''))
        full_statement.append(')')
        if opts.db_tablespace:
            tablespace_sql = connection.ops.tablespace_sql(
                    opts.db_tablespace)
            if tablespace_sql:
                full_statement.append(tablespace_sql)
        full_statement.append(';')
        final_output.append('\n'.join(full_statement))

        if opts.auto_field:
            # Add any extra SQL needed to support auto-incrementing primary
            # keys.
            auto_column = opts.auto_field.db_column or opts.auto_field.name
            autoinc_sql = connection.ops.autoinc_sql(opts.db_table,
                                                     auto_column)
            if autoinc_sql:
                for stmt in autoinc_sql:
                    final_output.append(stmt)

        return final_output, pending_references

    @classmethod
    def sql_indexes_for_model(self, model, style):
        """
        Returns the CREATE INDEX SQL statements for a single model.
        """
        if not model._meta.managed or model._meta.proxy or model._meta.swapped:
            return []
        output = []
        for f in model._meta.local_fields:
            output.extend(self.sql_indexes_for_field(model, f, style))
        for fs in model._meta.index_together:
            fields = [model._meta.get_field_by_name(f)[0] for f in fs]
            output.extend(self.sql_indexes_for_fields(model, fields, style))
        return output

    @classmethod
    def sql_indexes_for_field(self, model, f, style):
        """
        Return the CREATE INDEX SQL statements for a single model field.
        """
        if f.db_index and not f.unique:
            return self.sql_indexes_for_fields(model, [f], style)
        else:
            return []

    @classmethod
    def sql_indexes_for_fields(self, model, fields, style):
        if len(fields) == 1 and fields[0].db_tablespace:
            tablespace_sql = self.connection.ops.tablespace_sql(fields[0].db_tablespace)
        elif model._meta.db_tablespace:
            tablespace_sql = self.connection.ops.tablespace_sql(model._meta.db_tablespace)
        else:
            tablespace_sql = ""
        if tablespace_sql:
            tablespace_sql = " " + tablespace_sql

        field_names = []
        qn = self.connection.ops.quote_name
        for f in fields:
            field_names.append(style.SQL_FIELD(qn(f.column)))

        index_name = "%s_%s" % (model._meta.db_table, self._digest([f.name for f in fields]))

        return [
                style.SQL_KEYWORD("CREATE INDEX") + " " +
                style.SQL_TABLE(qn(truncate_name(index_name, self.connection.ops.max_name_length()))) + " " +
                style.SQL_KEYWORD("ON") + " " +
                style.SQL_TABLE(qn(model._meta.db_table)) + " " +
                "(%s)" % style.SQL_FIELD(", ".join(field_names)) +
                "%s;" % tablespace_sql,
        ]

    @classmethod
    def _digest(self, *args):
        """
        Generates a 32-bit digest of a set of arguments that can be used to
        shorten identifying names.
        """
        h = hashlib.md5()
        for arg in args:
            h.update(force_bytes(arg))
        return h.hexdigest()[:8]


class SqlModelMixin(object):

    @classmethod
    def get_create_model_indexs(cls):
        return SqlModel.sql_indexes_for_model(cls, no_style())

    @classmethod
    def get_create_model_sql(cls, replace_table_name='') -> str:
        """获取创建模型的SQL语句
        @replace_table_name 需要替换的表名
        """

        sql, _ = SqlModel.sql_create_model(cls, no_style())
        sql = sql[0].replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS').rstrip(';')
        sql = '%s ENGINE=InnoDB ;' % sql
        if replace_table_name:
            sql = sql.replace(cls._meta.db_table, replace_table_name)
        return sql

    @classmethod
    def get_db_name(cls):
        return settings.DATABASES.get(cls.objects.db, {}).get('NAME', '')

    @classmethod
    def get_app_name(cls):
        return cls._meta.app_label

    @classmethod
    def get_table_name(cls):
        """返回模型的表名
        """
        return cls._meta.db_table


class BaseModelMixin(SqlModelMixin):
    """
    基本模型
    """

    def is_related_field(self, field):
        return isinstance(field, (models.ForeignKey, models.ManyToManyField, models.OneToOneRel))

    def optimistic_save(self, *args, **kwargs):
        """
        乐观锁 保存
        :return:
        """
        if self.id:
            new_data = {f.name: getattr(self, f.name) for f in self.get_fields(has_private=True) if
                        not self.is_related_field(f)}
            del new_data['id']
            new_data['_version'] += 1
            new_data['update_datetime'] = datetime.datetime.now()
            has_save = self.__class__.objects.using(kwargs.get('using')).filter(id=self.id,
                                                                                _version=self._version,
                                                                                ).update(
                    **new_data)
            self._version = new_data['_version'] if has_save else self._version
            return has_save
        else:
            return self.save(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.update_datetime = datetime.datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    @classmethod
    def create_or_update_for_params(cls, params_dict, ignore_list=()):
        err_msg = ''
        model = None

        try:
            _id = int(params_dict.get('id', '') or 0)

            if _id:
                model = cls.objects.get(id=_id)
            else:
                model = cls()
            keys = params_dict.keys()
            for f in cls.get_fields():
                field_name = f.get_attname()
                if field_name in ignore_list or field_name == 'id' or field_name not in keys:
                    continue
                value = params_dict.get(field_name, None)

                value = f.to_python(value)
                if not (not f.null and value is None):
                    setattr(model, field_name, value)
        except Exception as e:
            logger.error(e)
            err_msg = trace_msg()
        return err_msg, model

    def is_attr_instance(self, attr, cla):
        return isinstance(getattr(self, attr), cla)

    def set_attrs_for_dict(self, dict_data):
        for f in self.get_fields(has_private=True):
            if isinstance(f, (models.ForeignKey, models.ManyToManyField, models.OneToOneRel)):
                continue
            data = dict_data.get(f.name, f.default)
            if not data is models.fields.NOT_PROVIDED:
                if not f.null and data is None:
                    data = f.default
                self.set_attr(f.name, data, null=True)

    def set_attr(self, name, value, value_handler=None, null=False):
        '''设置模型的属性
        '''

        if value_handler:
            value = value_handler(value)
        if not null:
            assert value != None and value != '', '%s 不能为空!' % self.get_verbose_name(name)
        setattr(self, name, value)

    def to_dict(self, ignore_list=(), has_m2mfields=False, is_msgpack=False):
        d = {}
        for field in self._meta.fields:
            attr = field.name
            attr_value = getattr(self, attr)

            # 特殊处理datetime的数据
            if isinstance(attr_value, datetime.datetime) and is_msgpack:
                d[attr] = attr_value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(attr_value, datetime.date):
                d[attr] = attr_value.strftime('%Y-%m-%d') and is_msgpack
            # 递归生成BaseModel类的dict
            elif isinstance(attr_value, BaseModel):
                d[attr] = attr_value.get_dict(has_m2mfields=has_m2mfields, is_msgpack=is_msgpack)
            elif isinstance(attr_value, (int, str, float)):
                d[attr] = getattr(self, attr)
            elif not is_msgpack:
                d[attr] = field.get_prep_value(getattr(self, attr))

        if has_m2mfields:
            m2mfields = self.__class__._meta.many_to_many
            if m2mfields:
                for m in m2mfields:
                    attr_name = m.attname
                    if hasattr(self, attr_name):
                        attlist = getattr(self, attr_name).all()
                        l = []
                        for attr in attlist:
                            if isinstance(attr, BaseModel):
                                l.append(attr.to_dict(is_msgpack=is_msgpack))
                            else:
                                dic = attr.__dict__
                                if '_state' in dic:
                                    dic.pop('_state')
                                l.append(dic)
                        d[attr_name] = l
        # 由于ManyToMany类不能存在于_meat.fields，因而子类需要在getMtMFiled中返回这些字段
        if 'basemodel_ptr' in d:
            d.pop('basemodel_ptr')

        if ignore_list:
            for m in ignore_list:
                if d.get(m) is not None:
                    d.pop(m)
        # 移除不需要的字段
        return d

    get_dict = to_dict

    def to_json(self, ignore_list=()):
        return json_dumps(self.to_dict(ignore_list))

    def get_verbose_name(self, field_name):
        """返回模型属性描述
        """
        for x in self.__class__.get_fields():
            if field_name == x.name:
                return x.verbose_name

    @classmethod
    def get_list_view_name(cls,model_class=None):
        model_class = model_class or cls
        return '%s.%s.list' % (model_class._meta.app_label, cls.get_lower_name(model_class))

    @classmethod
    def get_list_url(cls):
        return reverse(cls.get_list_view_name())

    @CachedClassAttribute
    def lower_name(cls):
        return cls.get_lower_name()

    @classmethod
    def get_lower_name(cls, model_class=None):
        new_lower_name_list = []
        name_str = model_class.__name__ if model_class else cls.__name__
        for i, c in enumerate(name_str):
            if i > 0 and c.isupper():
                if name_str[i - 1].islower() or name_str[i + 1].islower():
                    new_lower_name_list.append('_')
            new_lower_name_list.append(c.lower())
        return ''.join(new_lower_name_list)

    @classmethod
    def get_db_name(cls):
        return settings.DATABASES.get(cls.objects.db, {}).get('NAME', '')

    @classmethod
    def get_app_name(cls):
        return cls._meta.app_label

    @classmethod
    def get_table_name(cls):
        """返回模型的表名
        """
        return cls._meta.db_table

    @classmethod
    def get_fields_name_list(cls, ignore_keys=('id',)):
        return [f.get_attname() for f in cls.get_fields() if f.attname not in ignore_keys]

    @CachedClassAttribute
    def fields(cls):
        opts = cls._meta
        from django.db.models.fields import Field as ModelField
        from itertools import chain
        sortable_private_fields = [f for f in opts.private_fields if isinstance(f, ModelField)]
        return [f for f in sorted(chain(opts.concrete_fields, sortable_private_fields, opts.many_to_many))]

    @classmethod
    def get_fields(cls, has_private=False):
        """返回模型的相关字段定义
        """
        return [f for f in cls.fields if
                has_private or not f.name.startswith('_')]

    @classmethod
    def get_many_to_many_fileds(cls):
        return cls._meta.many_to_many

    @CachedClassAttribute
    def fields_map(cls):
        return cls.get_fields_map()

    @classmethod
    def get_fields_map(cls):
        field_dict = OrderedDict([(f.name, f) for f in cls.get_fields()])
        return field_dict

    @classmethod
    def prefetch_related_all(cls):
        return cls.objects.prefetch_related(*[f.attname for f in cls._meta.many_to_many])


class BaseModel(models.Model, BaseModelMixin):
    id = models.BigAutoField(primary_key=True)
    _version = models.IntegerField(_("版本"), default=0, null=False)
    # auto_now_add = True    #创建时添加的时间  修改数据时，不会发生改变
    create_datetime = models.DateTimeField(_("创建时间"), auto_now_add=True, blank=True)
    update_datetime = models.DateTimeField(_("更新时间"), auto_now=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['id']


class BaseNameModel(BaseModel):
    name = models.CharField(_('名称'), max_length=100, null=False, blank=False, validators=[LetterValidator],
                            unique=True)

    alias = models.CharField(_('别名'), max_length=100, default='', null=False, blank=True)

    class Meta:
        abstract = True


class JSONField(models.TextField):
    description = "Json"

    def __init__(self, *args, **kwargs):
        super(JSONField, self).__init__(*args, **kwargs)

    def to_python(self, value):

        if not isinstance(value, str):
            return value
        try:

            _r = json.loads(value)
        except Exception as e:
            logger.error('to_python Failed.', exc_info=e)
            _r = {}
        return _r

    def get_prep_value(self, value):
        try:
            if isinstance(value, str):
                json.loads(value)
                _v = value
            else:
                _v = json_dumps(value)
        except Exception as e:
            logger.error('get_prep_value Failed. %s' % value, exc_info=e)
            _v = '{}'
        return _v


class ObjectDictField(models.TextField):
    """ObjectDictField is a textfield that contains JSON-serialized dictionaries."""
    description = "ObjectDict"

    def __init__(self, *args, **kwargs):
        if not kwargs.get('default', None):
            kwargs['default'] = ObjectDict()
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression=None, connection=None):
        return self.to_python(value)

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""
        try:
            if isinstance(value, str):
                value = json.loads(value)
        except Exception as e:
            logger.error('to_python. %s' % value, exc_info=e)
            value = {}
        return ObjectDict(value)

    def get_prep_value(self, value):
        try:
            if isinstance(value, dict):
                return json_dumps(value)
            return value
        except Exception as e:
            logger.error('Failed. %s' % value, exc_info=e)
            return '{}'


serializers.ModelSerializer.serializer_field_mapping[ObjectDictField] = DictField
serializers.ModelSerializer.serializer_field_mapping[timezone_field.TimeZoneField] = CharField


def validate_re(value, pattern='', err_msg=''):
    if not re.match(pattern, value):
        raise ValidationError(err_msg)


def get_re_validate(pattern='', err_msg=''):
    """
    根据正则，返回参数验证函数

    :param pattern:
    :param err_msg:
    :return: partial
    """
    return RegexValidator(validate_re, err_msg)
