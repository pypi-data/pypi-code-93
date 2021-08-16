# -*- coding: utf-8 -*-
# @Time    : 2020-07-16 14:25
# @Author  : xzr
# @File    : settings
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :
from __future__ import absolute_import

from framework.conf import SettingOptions
from framework.translation import _

AUTH_USER_MODEL = 'myadmin.models.user.User'

ALLOW_REGISTER = SettingOptions(False, _('是否允许注册'), 'ALLOW_REGISTER','System')
ALLOW_REGISTER_ROLE_CHOICE = SettingOptions(False, _('注册时能否选择角色'), 'ALLOW_REGISTER_CHOICE','System')

USE_LDAP_AUTH = SettingOptions(False, _('是否使用LDAP验证'), 'USE_LDAP_AUTH', 'ldap')

LDAP_HOST = SettingOptions('ldaps://127.0.0.1:13891', 'LDAP 连接地址', 'LDAP_HOST', 'ldap')
_LDAP_BASE_DN = 'dc=bigdata,dc=com'
LDAP_BASE_DN = SettingOptions(_LDAP_BASE_DN, 'LDAP BASE_DN', 'LDAP_BASE_DN', 'ldap')

LDAP_BIND_DN = SettingOptions("cn=bigdata,ou=people,%s" % _LDAP_BASE_DN, 'LDAP 绑定账号', 'LDAP_BIND_DN', 'ldap')

LDAP_BIND_PASSWORD = SettingOptions("123", 'LDAP 绑定密码', 'LDAP_BIND_PASSWORD', 'ldap')

LDAP_USER_BASE_DN = SettingOptions("ou=people,%s" % _LDAP_BASE_DN, 'LDAP 用户域名', 'LDAP_USER_BASE_DN', 'ldap')

LDAP_USER_FILTER = SettingOptions('(objectClass=posixAccount)', 'LDAP 用户过滤条件', 'LDAP_USER_FILTER', 'ldap')

LDAP_GROUP_BASE_DN = SettingOptions("ou=role,%s" % _LDAP_BASE_DN, 'LDAP 组域', 'LDAP_GROUP_BASE_DN', 'ldap')

LDAP_GROUP_FILTER = SettingOptions('(objectClass=posixGroup)', 'LDAP 组过滤', 'LDAP_GROUP_FILTER', 'ldap')

LDAP_USER_ATTR_MAP = {
        "alias": "alias",
        "cn"   : "name",
        "email": "email",
}

LDAP_GROUP_ATTR_MAP = {
        "alias": "alias",
        "name" : "cn",
}


class SMS_CONFIG:
    AppKey = '1400029142'
    AppSecret = '122424d328d272fa85cc01d874fa5066'
    sms_free_sign_name = "游娱"
    sms_template_code = "16858"

from settings import *