# -*- coding: utf-8 -*-
# @Time    : 2019-09-03 11:49
# @Author  : xzr
# @File    : resource
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 资源 相关模型


import logging
import typing
from dataclasses import dataclass
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from framework.models import BaseModel
from framework.utils import trace_msg
from framework.utils.bitmap import BitMap
from framework.views import Request
from ..apps import MyadminConfig


class AbsResourceBackend(object):
    @classmethod
    def decode_members(cls, member_str): pass

    @classmethod
    def encode_members(cls, member_list): pass


class BitMapResourceBackend(AbsResourceBackend):
    """资源id 转为16进存储
    """

    @classmethod
    def decode_members(cls, member_str):
        return cls.hex2ids(member_str)

    @classmethod
    def encode_members(cls, member_list):
        return cls.ids2hex(member_list)

    @classmethod
    def ids2hex(cls, id_list):
        hex_str = ''
        if not id_list: return hex_str
        try:
            n_l = [int(x) for x in id_list]
            maxnum = max(n_l) + 1
            bm = BitMap(maxnum)
            bins = []
            for i in n_l:
                bm.set(i)

            hex_str = bm.tohexstring()
        except Exception as e:
            logging.error(trace_msg())

        finally:
            return hex_str

    @classmethod
    def hex2ids(cls, hex_str):
        id_list = set()
        if not hex_str: return id_list
        try:
            bm = BitMap.fromhexstring(hex_str)
            id_list.update(bm.nonzero())
        except Exception as e:
            logging.error(trace_msg())
        finally:
            return id_list


class StrResourceBackend(AbsResourceBackend):
    sep = ','

    @classmethod
    def decode_members(cls, member_str):
        return set(member_str.split(','))

    @classmethod
    def encode_members(cls, member_list):
        return cls.sep.join((str(x) for x in member_list))


def get_resource_backend(_str) -> AbsResourceBackend:
    if not _str or _str[0] == '0':
        return BitMapResourceBackend
    else:
        return StrResourceBackend


@dataclass
class ModelResource(object):
    """
    模型资源类
    """
    label = ''
    name = ''
    unique_filed_name = 'id'
    alias_lookup = 'alias'
    model_class: BaseModel = None
    template_context = {}
    default_template = 'myadmin/widgets/resource_checkbox.html'
    template = default_template
    help_text = ''
    is_inner = False

    def __init__(self):
        self.model_class = self.__class__.model_class

    @property
    def id_field_lookup(self):
        return '%s_%s' % (self.name, self.unique_filed_name)

    def get_q_condition(self, members_list):
        q = Q(**{'%s__in' % self.unique_filed_name: members_list})
        return q

    def get_resource_queryset(self, user_model):
        """
        获取资源查询
        :param user_model:
        :return:
        """
        model_resource_class = self.model_class

        if user_model.is_root:
            return model_resource_class.objects.all()
        return self.get_role_resource(user_model.get_roles())

    def get_role_resource(self, roles):
        """
        获取角色是所有的资源 ,资源成员 以 x,x,x 方式
        :param user_model:
        :return:
        """
        model_class = self.model_class

        resource_objs = Resource.objects.filter(role__in=roles, name=self.name)
        try:
            if len(resource_objs) == 1:
                resource_ids = resource_objs[0].members
            else:
                resource_ids = reduce(lambda x, y: y | x, resource_objs)
        except TypeError as e:
            resource_ids = []
        q = self.get_q_condition(resource_ids)
        return model_class.objects.filter(q).distinct()

    def create_resource(self, role_model, members_list):
        """创建资源"""
        resource: Resource = role_model.get_resource_model(self.name)
        resource.members = members_list
        resource.save()
        role_model.resource.add(resource)

    def get_template_context(self, request: Request):
        """
        获取模板上下文
        :param request:
        :return:
        """
        return {}

    def members_handle(self, members):
        """ """
        return {int(i) for i in members}



class RelaRtionModelResource(ModelResource):
    """关联模型资源,需要在 model 上定义 role = models.ManyToManyField(Role, verbose_name=_('允许访问的角色')) 字段
    """
    role_field_name = 'role'
    related_field = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_has_role_many_to_many()

    def check_has_role_many_to_many(self):
        from myadmin.models import Role
        for field in self.model_class._meta.many_to_many:
            if field.related_model is Role:
                self.role_field_name = field.attname
                self.related_field = field
                return
        raise Exception(
                '''需要在 %s model 上定义 role = models.ManyToManyField(Role, verbose_name=_('允许访问的角色')) 字段''' % self.model_class)

    def get_role_q(self, roles):
        return Q(**{'%s__in' % self.role_field_name: roles})

    def get_resource_queryset(self, user_model):
        """
        获取资源查询,使用 xxx_set 的方式
        :param user_model:
        :return:
        """
        roles = user_model.get_roles()

        model_resource_class: BaseModel = self.model_class
        if user_model.is_root:
            return model_resource_class.objects.all()
        return self.get_role_resource(roles)

    def get_role_resource(self, roles):
        return self.model_class.objects.filter(self.get_role_q(roles)).distinct()

    def create_resource(self, role_model, members_list):
        """关联模型,反向添加角色
        使用 role_model.xxx_set.set(members_list, clear=True)
        """
        if not role_model.id:
            role_model.save()
        m2m_field_name = '%s_set' % self.model_class._meta.model_name
        getattr(role_model, m2m_field_name).set(self.members_handle(members_list))



class Resource(BaseModel):
    """资源
    """
    _resource_map: typing.Dict[
        str, ModelResource] = {}  # {"server":Server,"channel":Channel,"agent":Agent,"server_group":Group}

    name = models.CharField(_("资源名"), max_length=20, null=False, help_text=_('资源简称,只允许字母'))
    role_id = models.IntegerField(_('角色id'), null=True)
    _members = models.TextField(_('资源对象成员列表'))
    __members_cache = None

    has_all_resosurce_mark = '__all__'

    class Meta:
        app_label = MyadminConfig.name
        unique_together = (
                ('name', 'role_id'),  # 联合唯一
        )

    @property
    def data_url(self):
        self.__class__._resource_map.get(self.name).model_class.get_list_url()

    def add_member(self, id_or_ids):
        if not isinstance(id, list):
            id_or_ids = [id_or_ids]
        id_or_ids = set(id_or_ids)
        new_ids = self.members
        new_ids |= id_or_ids
        self.members = new_ids

    @property
    def members(self):
        """将16进数据返回id列表
        """
        if self.__members_cache is None:
            _members = get_resource_backend(self._members).decode_members(self._members)
            self.__members_cache = self._resource_map.get(self.name, ModelResource()).members_handle(_members)
        return self.__members_cache

    @members.setter
    def members(self, id_list):
        if not isinstance(id_list, (list, set)):
            id_list = [id_list]
        self._members = StrResourceBackend.encode_members(id_list)

    def __or__(self, other):
        """与位
        @other为资源对象或者资源的成员set表
        """
        if isinstance(other, Resource):
            return self.members.union(other.members)
        return self.members.union(other)

    @classmethod
    def register(cls, model_resource: ModelResource):
        """
        注册资源
        :param modle_name:  名
        :param model_cls:   模型
        :return:
        """
        assert isinstance(model_resource, ModelResource), '%s is not ModelResource subclass ' % model_resource
        assert not model_resource.name in cls._resource_map, 'The same %s already exists' % model_resource.name

        cls._resource_map[model_resource.name] = model_resource

    @classmethod
    def get_resource_map(cls):
        return cls._resource_map

    @classmethod
    def get_model_class(cls, name) -> models.Model:
        return cls.get_model_resource(name).model_class

    @classmethod
    def get_model_resource(cls, name) -> ModelResource:
        return cls._resource_map[name]


class ResourceProxy(object):
    """资源代理,为了在模版里可以使用request.user.resource.xxx
    """

    def __init__(self, user_obj):
        self.user_obj = user_obj

    def get_model_resource_map(self):
        return Resource.get_resource_map()

    def __getattr__(self, name):
        if name != 'user_obj':
            return self.user_obj.get_resource(name)
        else:
            return super(ResourceProxy, self).__getattr__(name)
