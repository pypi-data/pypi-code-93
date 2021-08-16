# -*- coding: utf-8 -*-
# @Time    : 2020-09-15 14:35
# @Author  : xzr
# @File    : user_resource
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

from framework.translation import _
from myadmin.models.resource import RelaRtionModelResource, Resource
from .models import AccessDomain


class AccessDomainModelResource(RelaRtionModelResource):
    label = _('LDAP 访问域')
    name = 'access_domain'
    model_class = AccessDomain
    template = RelaRtionModelResource.default_template


Resource.register(AccessDomainModelResource())
