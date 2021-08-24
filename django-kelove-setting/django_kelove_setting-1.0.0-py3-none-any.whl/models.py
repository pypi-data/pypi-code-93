"""
models.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/24/21 11:16 AM
"""

from django.conf import settings
from django.contrib.auth.models import Permission
from django.db import models
from django.contrib.auth import get_permission_codename
from django.contrib.admin.options import get_content_type_for_model
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class Settings(models.Model):
    """
    配置表
    """

    settings_key = models.CharField(
        verbose_name=_('配置标识'),
        unique=True,
        db_index=True,
        max_length=191,
        blank=False,
        null=False
    )

    settings_title = models.CharField(
        verbose_name=_('配置名称'),
        max_length=191,
        default='',
        blank=True,
        null=False
    )

    settings_val = models.JSONField(
        verbose_name=_('配置内容'),
        default=dict,
        null=False,
        blank=True
    )

    # 创建用户
    created_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('创建用户'),
        related_name="%(app_label)s_%(class)s_created_user_set",
        on_delete=models.SET_NULL,
        db_constraint=False,
        null=True,
        blank=True,
        editable=False,
        default=None
    )

    # 更新用户
    updated_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('更新用户'),
        related_name="%(app_label)s_%(class)s_updated_user_set",
        on_delete=models.SET_NULL,
        db_constraint=False,
        null=True,
        blank=True,
        editable=False,
        default=None
    )

    # 创建时间
    created_time = models.DateTimeField(verbose_name=_('创建时间'), auto_now_add=True, editable=True)

    # 更新时间
    updated_time = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    def get_settings_permission_codename(self, action):
        """
        获取配置权限代码
        :param action:
        :return:
        """

        return get_permission_codename(action, self._meta) + '_{key}'.format(key=self.settings_key)

    def get_settings_permission_code(self, action):
        """
        获取配置权限代码(包括app label)
        :param action:
        :return:
        """

        return "%s.%s" % (self._meta.app_label, self.get_settings_permission_codename(action))

    def create_admin_settings_auth(self):
        """
        初始化配置权限
        :return:
        """

        content_type = get_content_type_for_model(self)

        change_obj, is_create = Permission.objects.get_or_create(
            codename=self.get_settings_permission_codename('change'),
            content_type=content_type,
        )
        if is_create or not change_obj.name:
            change_obj.name = 'Can change {value}'.format(value=self.settings_title)
            change_obj.save()

        delete_obj, is_create = Permission.objects.get_or_create(
            codename=self.get_settings_permission_codename('delete'),
            content_type=content_type,
        )
        if is_create or not delete_obj.name:
            delete_obj.name = 'Can delete {value}'.format(value=self.settings_title)
            delete_obj.save()

        view_obj, is_create = Permission.objects.get_or_create(
            codename=self.get_settings_permission_codename('view'),
            content_type=content_type,
        )
        if is_create or not view_obj.name:
            view_obj.name = 'Can view {value}'.format(value=self.settings_title)
            view_obj.save()

    def delete_admin_settings_auth(self):
        """
        删除配置权限
        :return:
        """

        content_type = get_content_type_for_model(self)
        Permission.objects.filter(
            codename__in=[
                self.get_settings_permission_codename('change'),
                self.get_settings_permission_codename('delete'),
                self.get_settings_permission_codename('view')
            ],
            content_type=content_type,
        ).delete()

    def __str__(self):
        return '%s | %s' % (self.settings_title, self.settings_key)

    class Meta:
        verbose_name = _('应用配置')
        verbose_name_plural = _('应用配置')


@receiver(post_save, sender=Settings)
def update_form_cache(sender, instance, created, **kwargs):
    """
    配置更新时同时更新缓存
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """

    # 更新缓存
    from .utils import get_settings_form_class
    form = get_settings_form_class(form_class=instance.settings_key)
    if form:
        form.delete_cache()


@receiver(pre_delete, sender=Settings)
def delete_admin_settings_auth_cache(sender, instance, **kwargs):
    """
    配置删除之前，删除配置对应的权限及缓存
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """

    # 删除权限
    instance.delete_admin_settings_auth()

    # 更新缓存
    from .utils import get_settings_form_class
    form = get_settings_form_class(form_class=instance.settings_key)
    if form:
        form.delete_cache()
