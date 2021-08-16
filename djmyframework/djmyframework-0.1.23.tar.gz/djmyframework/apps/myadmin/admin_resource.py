# -*- coding: utf-8 -*-
# @Time    : 2020-09-15 14:35
# @Author  : xzr
# @File    : user_resource
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

from framework.translation import _
from .models import Menu, ModelResource, Resource, Role, User,RelaRtionModelResource


class UserModelResource(RelaRtionModelResource):
    name = 'user'
    label = _('管理的用户')
    model_class = User
    is_inner = True

    def get_resource_queryset(self, user_model):
        return user_model.get_manageable_user()


class RoleModelResource(ModelResource):
    name = 'role'
    label = _('管理的角色')
    model_class = Role
    is_inner = True


class MenuModelResource(ModelResource):
    label = _('管理的菜单权限')
    unique_filed_name = 'name'
    name = 'menu'
    model_class = Menu
    is_inner = True

    def members_handle(self, members):
        """菜单是返回 menu1,menu2,,menu3 的字符串列表"""
        return members


Resource.register(UserModelResource())
Resource.register(RoleModelResource())
Resource.register(MenuModelResource())
