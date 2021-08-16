# -*- coding: utf-8 -*-
# @Time    : 2019-09-03 11:49
# @Author  : xzr
# @File    : resource
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 角色 相关模型
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from framework.models import BaseModel
from framework.utils.cache import CacheAttribute
from framework.utils.myenum import Enum
from ..apps import MyadminConfig
from .resource import Resource


class RoleManagerMixin(object):

    def get_resource_model(self, name):
        resource_model, created = Resource.objects.get_or_create(name=name, role_id=self.id)
        return resource_model

    def add_resource_member(self, name, id):
        '''增加资源对象
        @name  资源名
        @id    资源对象id
        '''
        resource_obj = self.get_resource_model(name)
        if resource_obj:
            resource_obj.add_member(id)
            resource_obj.save()

    def get_resource(self, name):
        return Resource.get_model_resource(name).get_role_resource([self])

    def create_resource(self, name, id_list):
        '''角色创建资源
        @资源名
        @id列表
        '''

        if id_list is None:
            return
        if not self.id:  # 新建时没有对象,先保存一下
            self.save()
        model_resource = Resource.get_model_resource(name)
        model_resource.create_resource(self, id_list)

    @classmethod
    def create_role_from_name(cls, name):
        _role, _c = cls.objects.get_or_create(name=name)
        return _role

    @classmethod
    def create_default_role(cls):
        from config.role import RoleList
        for name, alias, _type, parent_name in RoleList:
            _role = cls.create_role_from_name(name)
            _role.alias = alias
            _role.type = _type
            if parent_name:
                parent_role = cls.create_role_from_name(parent_name)
            else:
                parent_role = None
            _role.parent = parent_role
            _role.save()
            print(alias)


class Role(RoleManagerMixin, BaseModel):
    """角色模型
    """

    class RoleType(Enum):
        USER = 1, _('角色')
        GROUP = 2, _('组织')
        PERMISSION = 3, _('权限集合')

    alias = models.CharField('角色名称', max_length=50)

    name = models.CharField('标识', max_length=50, unique=True, db_index=True,
                            validators=[RegexValidator(r'^[a-z][\d\w_]+$', _('字母组合,符合^[a-z][\d\w_]+$'))])

    parent = models.ForeignKey(to='self', verbose_name=_("上级"), on_delete=models.SET_NULL, null=True)
    resource = models.ManyToManyField(Resource, verbose_name=_('资源对象'), blank=True)
    type = models.IntegerField(_('类型'), default=1, choices=RoleType.member_list())
    remark = models.TextField(_('描述'), default='', max_length=1000, blank=True)
    creater = models.ForeignKey('myadmin.User', verbose_name=_("创建者"), on_delete=models.DO_NOTHING, null=True,
                                related_name='user_id')
    home_index = models.CharField(_('角色首页'), default='/home', max_length=500)

    __resource_ids_cache = None

    class Meta:
        app_label = MyadminConfig.name

    @CacheAttribute
    def type_alias(self):
        if self.id:
            return self.get_type_display()

    def get_resource_members(self, name):
        model_resource = Resource.get_model_resource(name)
        return model_resource.get_role_resource([self]).values_list(
                model_resource.unique_filed_name,
                flat=True)

    @CacheAttribute
    def resource_ids(self):
        resource_map_ids = {}
        if self.id:
            resource_map_ids = {r.name: r.members for r in self.resource.all()}
            for resource_name, model_resource in Resource.get_resource_map().items():
                if resource_map_ids.get(resource_name, None) is None:
                    resource_map_ids[resource_name] = model_resource.get_role_resource([self]).values_list(
                            model_resource.unique_filed_name,
                            flat=True)
        return resource_map_ids

    resource_map_ids = resource_ids

    def save(self, *args, **kwargs):
        super(Role, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for r in self.resource.all():
            r.delete()
        self.resource.clear()
        super(Role, self).delete(*args, **kwargs)

    def __unicode__(self):
        return '%s' % self.name

    def __str__(self):
        return '%s' % self.name
