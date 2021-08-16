# -*- coding: utf-8 -*-
# @Time    : 2019-09-03 11:49
# @Author  : xzr
# @File    : resource
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 系统 :管理员 相关模型
import base64
import datetime
import time

import passlib.hash
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from framework.models import BaseModel, JSONField
from framework.utils.cache import CacheAttribute
from framework.utils.myenum import Enum
from framework.validators import LetterValidator
from .resource import Resource, ResourceProxy
from .role import Role
from ..apps import MyadminConfig
from framework.utils.log import logger

class UserManagerMixin(object):
    """用户管理者,扩展admin模型的方法
    """

    def __init__(self, *args, **kwargs):
        # self.resource = ResourceProxy(self)
        super(UserManagerMixin, self).__init__(*args, **kwargs)
        self.__resource_map = {}
        self.__cache_roles = None

    @property
    def resource(self) -> Resource:
        return ResourceProxy(self)

    def get_role_index(self):
        for r in self.get_roles():
            if r.index:
                return r.index
        else:
            return ''

    @classmethod
    def get_normal_user_list(cls):
        return User.objects.filter(status=User.Status.NORMAL)

    @classmethod
    def get_user(cls, user_id):
        """获取管理员
        """
        return cls.objects.filter(id=user_id).prefetch_related('role').first()

    def check_role(self, name):
        for r in self.get_roles():
            if r.name == name:
                return True
        return False

    @CacheAttribute
    def is_root(self):
        """是否超级管理员
        """
        return self.check_role('root')

    @CacheAttribute
    def is_sdk_manager(self):
        return self.check_role('sdk_manager')

    @CacheAttribute
    def is_yunying(self):
        return self.check_role('yunying')

    @property
    def is_agent(self):
        """是否渠道用户
        """
        return self.id < 0

    @property
    def is_channel_user(self):
        return self.is_agent

    @CacheAttribute
    def is_kefu(self):
        """是否客服
        """
        return self.check_role('kefu')

    @property
    def is_not_active(self):
        return self.status == User.Status.NotActive

    @CacheAttribute
    def is_manager(self):
        """是否管理员
        """
        return self.is_root or self.check_role('manager') or self.get_manageable_user().exists()

    def get_manageable_user(self):
        """获取自己的下属,除权限集合 如果是管理员这不能获取到
        """
        return User.objects.filter(
                role__in=self.get_resource('role').exclude(type=Role.RoleType.PERMISSION)).prefetch_related(
                'role').distinct()

    def get_resource_attrs(self, resource_name, attr_name, input_list=None, allow_none=False):
        input_list = input_list or []
        input_list = set([str(x) for x in input_list])
        resource_attrs = set([str(x) for x in self.get_resource(resource_name).values_list(attr_name, flat=True)])
        if allow_none and input_list:
            new_attrs = list((input_list & resource_attrs))
        else:
            new_attrs = list((input_list & resource_attrs) or resource_attrs)
        return new_attrs

    def get_resource_ids(self, name, input_list=None):
        return self.get_resource_attrs(name, 'id', input_list)

    def set_resource(self, name, query_set):
        """设置资源,平台登录时就设置资源了
        """
        self.__resource_map[name] = query_set

    def get_resource(self, name):
        """按资源名获取所属角色相应的资源
        """
        _r = self.__resource_map.get(name, None)
        if _r == None:
            _r = self._get_resource(name)
        self.__resource_map[name] = _r
        return self.__resource_map[name]

    def _get_resource(self, name):
        return Resource.get_model_resource(name).get_resource_queryset(self)

    _get_resource_from_model = _get_resource

    def get_roles(self):
        """获取角色
        """
        if self.id:
            if self.__cache_roles != None:
                return self.__cache_roles
            self.__cache_roles = self.role.all()
            return self.__cache_roles
        else:
            return []

    @classmethod
    def create_role_from_name(cls, name):
        _role, _c = Role.objects.get_or_create(name=name)
        return _role

    @classmethod
    def create_root(cls):
        """创建系统管理员root账户
        """
        super_role, _c = Role.objects.get_or_create(name='root')
        user, _c = cls.objects.get_or_create(alias="系统管理员", username='root')
        user.role_ids = [super_role.id]
        user.status = cls.Status.NORMAL
        user.set_password('123456')
        user.save()

        logger.info('创建相关角色后,请务必删除root账户!')
        return user


class User(BaseModel, AbstractBaseUser, UserManagerMixin):
    """用户模型
    """
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Status(Enum):
        NORMAL = (0, _('正常'))
        LOCK = (1, _('锁定'))
        DELETED = (2, _('删除'))
        NotActive = (3, _('未激活'))
        Error = (4, _('错误'))
        LEAVE_OFFICE = (5, _('离职'))

    class UserType(Enum):
        NORMAL = (0, _('正常'))  # 正常用户
        CHANNEL = (1, _('渠道'))  # 渠道用户

    is_staff = False
    role = models.ManyToManyField(Role, verbose_name=_('所属角色'), blank=True)
    alias = models.CharField(_('别名'), max_length=50, db_index=True)

    username = models.CharField(_('用户名'), max_length=50, db_index=True, unique=True, validators=[LetterValidator])
    password = models.CharField('密码', max_length=64, db_index=True, blank=True, validators=[])
    last_ip = models.CharField(_('最后登录ip'), max_length=20, default='', blank=True)
    reg_ip = models.CharField('注册IP', max_length=20, default='', blank=True)
    last_time = models.DateTimeField(_('最后登录时间'), auto_now_add=True)
    login_count = models.IntegerField(_('登录次数'), default=0, blank=True)
    status = models.IntegerField(_('状态'), default=Status.NotActive, choices=Status.member_list(), help_text='登录状态')
    session_key = models.CharField(_('会话key'), max_length=40, db_index=True, default='', blank=True, null=False)

    class Meta:
        app_label = MyadminConfig.name
        ordering = ['id']

    # # @property
    # # def is_anonymous(self):
    # #     return True
    #
    # @property
    # def is_authenticated(self):
    #     return False

    def get_username(self):
        return self.username

    role_ids = []  # 保存角色id列表

    def __unicode__(self):
        return '%s' % self.username

    @property
    def role_alias(self):
        return [r.alias for r in self.get_roles()]

    @property
    def home_index(self):
        for role in self.get_roles():
            return role.home_index

    def get_ldap_ssha_encrypt_password(self, password_str):
        return passlib.hash.ldap_salted_sha1.encrypt(password_str)

    def check_ldap_ssha(self, source_str):
        from framework.utils import sshaDigest
        raw = base64.decodestring(self.password[len(b'{SSHA}'):])
        salt = raw[20:]
        got = sshaDigest(source_str, salt)
        return self.password == got

    def must_change_password(self):
        from framework.validators import PasswordValidator
        try:
            return PasswordValidator(self._password)
        except Exception as errors:
            return errors

    @property
    def is_active(self):
        return self.status == self.Status.NORMAL

    @CacheAttribute
    def has_bind_weixin(self):
        """是否已绑定微信"""
        return UserOauth.objects.filter(oauth_type='weixin', user_id=self.id).exists()

    @CacheAttribute
    def has_bind_phone(self):
        """是否已绑定手机"""
        return UserInfo.objects.filter(user=self).exclude(phone='').exists()

    @CacheAttribute
    def has_bind_weixin_phone_permission(self):
        return self.check_permission_for_name([u'绑定微信', u'绑定手机'])

    def check_permission_for_name(self, name_list):
        """是否有访问权限"""
        return self.resource.menu.using('read').filter(name__in=name_list).exists()

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)  # 新建时没有对象,先保存一下
        if not self.id:
            UserInfo.objects.get_or_create(user=self)
        if self.role_ids:  # 如果角色的列表存在,就保存
            self.role.clear()
            self.role.add(*Role.objects.filter(id__in=self.role_ids))

    def make_password(self, raw_password):
        self.set_password(raw_password)
        return self.password

    @classmethod
    def login_user(cls, request, the_user):
        """

        :type the_user: User
        """
        from django.contrib.auth import login
        request.session.clear()
        login(request, the_user)
        the_user.login_count += 1
        the_user.last_time = datetime.datetime.now()
        the_user.last_ip = request.real_ip
        the_user.session_key = request.session.session_key
        the_user.save()

    @property
    def is_ldap(self):
        return hasattr(self, 'ldap_attr_map')

    @CacheAttribute
    def user_info(self):
        user_info = None
        if self.id:
            user_infos = self.userinfo_set.all()
            if len(user_infos) >= 1:
                user_info = user_infos[0]
            else:
                user_info, _ = self.userinfo_set.get_or_create()
        return user_info

    @property
    def email(self):
        if self.user_info:
            return self.user_info.email

    @email.setter
    def email(self, emial):
        if self.user_info:
            self.user_info.email = emial
            self.user_info.save()


class UserInfo(BaseModel):
    """管理员信息
    """

    class Sex(Enum):
        UnKnow = 3, _('未知')
        Woman = 0, _('女')
        Man = 1, _('男')

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('所属管理员'))
    employee_id = models.CharField(_('工号'), max_length=15, null=False, default='', blank=True, db_index=True)
    sex = models.IntegerField(_('性别'), choices=Sex.member_list(), default=Sex.UnKnow, null=False)
    email = models.EmailField(_('邮件地址'), null=False, default='', blank=True)
    email_active = models.BooleanField(_('是否激活邮箱'), null=False, default=False)
    qq = models.CharField('QQ', max_length=15, null=False, default='', blank=True)
    phone = models.CharField(_('电话'), max_length=18, default='', db_index=True, null=False, blank=True)
    phone_active = models.BooleanField(_('是否绑定手机'), null=False, default=False)

    @CacheAttribute
    def user_alias(self):
        return self.user.alias

    class Meta:
        app_label = MyadminConfig.name


class UserOauth(BaseModel):
    """第三方登录关联表
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('所属管理员'), null=True)
    oauth_type = models.CharField(verbose_name=_('Oauth类型'), max_length=20)
    oauth_id = models.CharField(verbose_name=_('Oauth 账号ID'), max_length=128, db_index=True)
    access_token = models.CharField(verbose_name=_('access_token'), max_length=512)
    expires_timestamp = models.IntegerField(verbose_name=_('过期时间戳'), default=time.time)

    other_info = JSONField(verbose_name=_('其他信息'), default='{}')

    class Meta:
        app_label = MyadminConfig.name
        # db_table = u'user_oauth'
