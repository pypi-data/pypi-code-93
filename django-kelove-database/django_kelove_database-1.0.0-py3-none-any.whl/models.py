"""
models.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/2/21 10:32 AM
"""

from uuid import uuid4

from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth.models import Permission
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db import models

from .db.fields import JSONField
from .util import Units


def uuid_string(prefix: str = '') -> str:
    """
    生成uuid字符串
    :param prefix:
    :return:
    """

    _uuid_str = str(uuid4().hex)
    _uuid_str = 'u' + prefix + _uuid_str[:5] + _uuid_str[-4:]
    return _uuid_str.lower()


CK_FINDER_RESOURCE_ADAPTER_LOCAL = 'django_kelove_database.ckfinder.adapter.LocalAdapter'

CK_FINDER_RESOURCE_ADAPTER = (
    (CK_FINDER_RESOURCE_ADAPTER_LOCAL, _('本地存储')),
)


class CkfinderResource(models.Model):
    """
    Ckfinder 资源
    """

    permissions = {
        'ck_finder_folder_view': '浏览目录',
        'ck_finder_folder_create': '创建目录',
        'ck_finder_folder_rename': '重命名目录',
        'ck_finder_folder_delete': '删除目录',
        'ck_finder_file_view': '浏览文件',
        'ck_finder_file_create': '创建文件',
        'ck_finder_file_rename': '重命名文件',
        'ck_finder_file_delete': '删除文件',
        'ck_finder_image_resize': '生成缩略图',
        'ck_finder_image_resize_custom': '自定义缩略图大小'
    }

    adapter = models.CharField(
        verbose_name=_('资源类型'),
        max_length=191,
        choices=CK_FINDER_RESOURCE_ADAPTER,
        default=CK_FINDER_RESOURCE_ADAPTER_LOCAL,
        null=False,
        blank=False,
    )

    name = models.CharField(
        verbose_name=_('资源标识'),
        max_length=191,
        unique=True,
        db_index=True,
        default=uuid_string,
        null=False,
        blank=False
    )

    path = models.CharField(
        verbose_name=_('资源路径'),
        max_length=191,
        default='',
        null=False,
        blank=True,
        help_text='可使用的常量: {BASE_DIR} 、{STATIC_ROOT} 、{STATIC_URL} 、{MEDIA_ROOT} 、{MEDIA_URL} 例如：{MEDIA_ROOT}/demo01'
    )

    url = models.CharField(
        verbose_name=_('资源链接地址'),
        max_length=191,
        default='',
        null=False,
        blank=True,
        help_text='可使用的常量: {BASE_DIR} 、{STATIC_ROOT} 、{STATIC_URL} 、{MEDIA_ROOT} 、{MEDIA_URL} 例如：{MEDIA_URL}demo01/'
    )

    allowed_extensions = models.TextField(
        verbose_name=_('允许上传的文件后缀'),
        default='',
        null=False,
        blank=True,
        help_text='多个后缀名需用 "," 分割，例如：jpg,gif,png'
    )

    denied_extensions = models.TextField(
        verbose_name=_('禁止上传的文件后缀'),
        default='',
        null=False,
        blank=True,
        help_text='多个后缀名需用 "," 分割，例如：jpg,gif,png'
    )

    max_size = models.CharField(
        verbose_name=_('允许上传文件的最大尺寸'),
        max_length=191,
        default='0',
        null=False,
        blank=True,
        help_text='0表示不限制大小，可选单位：' + ' , '.join(Units.kib_units + Units.kb_units + Units.b_units) + ' 例如：5MiB'
    )

    other = JSONField(
        verbose_name=_('更多配置'),
        default=dict,
        null=False,
        blank=True
    )

    # 是否启用
    enabled = models.BooleanField(
        verbose_name=_('是否启用'),
        default=True,
        db_index=True,
        null=False,
        blank=False
    )

    # 是否验证用户权限
    verify_permissions = models.BooleanField(
        verbose_name=_('是否验证用户权限'),
        default=True,
        db_index=True,
        null=False,
        blank=False
    )

    ck_finder_folder_view = models.BooleanField(
        verbose_name=_('是否允许' + permissions['ck_finder_folder_view']),
        default=True,
        null=False,
        blank=False,
        help_text=_('不验证用户权限时生效')
    )

    ck_finder_folder_create = models.BooleanField(
        verbose_name=_('是否允许' + permissions['ck_finder_folder_create']),
        default=True,
        null=False,
        blank=False,
        help_text=_('不验证用户权限时生效')
    )

    ck_finder_folder_rename = models.BooleanField(
        verbose_name=_('是否允许' + permissions['ck_finder_folder_rename']),
        default=True,
        null=False,
        blank=False,
        help_text=_('不验证用户权限时生效')
    )

    ck_finder_folder_delete = models.BooleanField(
        verbose_name=_('是否允许' + permissions['ck_finder_folder_delete']),
        default=True,
        null=False,
        blank=False,
        help_text=_('不验证用户权限时生效')
    )

    ck_finder_file_view = models.BooleanField(
        verbose_name=_('是否允许' + permissions['ck_finder_file_view']),
        default=True,
        null=False,
        blank=False,
        help_text=_('不验证用户权限时生效')
    )

    ck_finder_file_create = models.BooleanField(
        verbose_name=_('是否允许' + permissions['ck_finder_file_create']),
        default=True,
        null=False,
        blank=False,
        help_text=_('不验证用户权限时生效')
    )

    ck_finder_file_rename = models.BooleanField(
        verbose_name=_('是否允许' + permissions['ck_finder_file_rename']),
        default=True,
        null=False,
        blank=False,
        help_text=_('不验证用户权限时生效')
    )

    ck_finder_file_delete = models.BooleanField(
        verbose_name=_('是否允许' + permissions['ck_finder_file_delete']),
        default=True,
        null=False,
        blank=False,
        help_text=_('不验证用户权限时生效')
    )

    ck_finder_image_resize = models.BooleanField(
        verbose_name=_('是否允许' + permissions['ck_finder_image_resize']),
        default=True,
        null=False,
        blank=False,
        help_text=_('不验证用户权限时生效')
    )

    ck_finder_image_resize_custom = models.BooleanField(
        verbose_name=_('是否允许' + permissions['ck_finder_image_resize_custom']),
        default=True,
        null=False,
        blank=False,
        help_text=_('不验证用户权限时生效')
    )

    def get_rule(self, permissions):
        return {
            "role": "*",
            "resourceType": self.name,
            "folder": "/",
            'FOLDER_VIEW': self.verify_permission(permissions, 'ck_finder_folder_view'),
            'FOLDER_CREATE': self.verify_permission(permissions, 'ck_finder_folder_create'),
            'FOLDER_RENAME': self.verify_permission(permissions, 'ck_finder_folder_rename'),
            'FOLDER_DELETE': self.verify_permission(permissions, 'ck_finder_folder_delete'),
            'FILE_VIEW': self.verify_permission(permissions, 'ck_finder_file_view'),
            'FILE_CREATE': self.verify_permission(permissions, 'ck_finder_file_create'),
            'FILE_RENAME': self.verify_permission(permissions, 'ck_finder_file_rename'),
            'FILE_DELETE': self.verify_permission(permissions, 'ck_finder_file_delete'),
            'IMAGE_RESIZE': self.verify_permission(permissions, 'ck_finder_image_resize'),
            'IMAGE_RESIZE_CUSTOM': self.verify_permission(permissions, 'ck_finder_image_resize_custom'),
        }

    def verify_permission(self, permissions, action):
        has_manage_permission = self.get_permission_code('manage_ckfinderresource', with_pk=False)
        if has_manage_permission in permissions:
            return True
        if not self.verify_permissions:
            return getattr(self, action)
        return self.get_permission_code(action) in permissions

    def create_permissions(self):
        """
        生成权限
        :return:
        """

        resource_title = self.name

        content_type = get_content_type_for_model(self)

        for permission_name, permission_title in self.permissions.items():
            obj, is_create = Permission.objects.get_or_create(
                codename=self.get_permission_codename(permission_name),
                content_type=content_type,
            )
            obj.name = f'{permission_title}-{resource_title}'
            obj.save()

    def delete_permissions(self):
        """
        删除权限
        :return:
        """
        content_type = get_content_type_for_model(self)
        Permission.objects.filter(
            codename__in=[
                self.get_permission_codename(permission_name)
                for permission_name, permission_title
                in self.permissions.items()
            ],
            content_type=content_type,
        ).delete()

    def get_permission_codename(self, action, with_pk=True):
        if not with_pk:
            return action
        resource_pk = self.pk
        return f'{action}_{resource_pk}'

    def get_permission_code(self, action, with_pk=True):
        """
        获取配置权限代码(包括app label)
        :param with_pk:
        :param action:
        :return:
        """

        return "%s.%s" % (self._meta.app_label, self.get_permission_codename(action=action, with_pk=with_pk))

    def get_resource(self):
        """
        :return:
        """

        default_info = {
            "adapter": self.adapter,
            "name": self.name,
            "path": self.replace_const(self.path),
            "url": self.replace_const(self.url),
            "allowed_extensions": self.get_extensions(self.allowed_extensions),
            "denied_extensions": self.get_extensions(self.denied_extensions),
            "max_size": float(Units.convert(string_value=self.max_size, unit=Units.B, decimals=0)[0]),
        }

        return {
            **self.other,
            **default_info
        }

    @classmethod
    def replace_const(cls, string: str) -> str:
        """
        常量替换
        :return:
        """
        return string.format(
            BASE_DIR=getattr(settings, 'BASE_DIR', ''),
            STATIC_ROOT=getattr(settings, 'STATIC_ROOT', ''),
            STATIC_URL=getattr(settings, 'STATIC_URL', ''),
            MEDIA_ROOT=getattr(settings, 'MEDIA_ROOT', ''),
            MEDIA_URL=getattr(settings, 'MEDIA_URL', ''),
        )

    @classmethod
    def get_extensions(cls, extensions: str) -> list:
        extensions = str(extensions).split(',') if extensions else []
        return [str(extension).lower() for extension in extensions]

    def __str__(self):
        return f'{self.name}({self.get_adapter_display()})'

    class Meta:
        verbose_name = _('Ckfinder 资源')
        verbose_name_plural = _('Ckfinder 资源')
        permissions = (
            ('manage_ckfinderresource', '文件管理'),
        )


@receiver(post_save, sender=CkfinderResource)
def create_auth(sender, instance, created, **kwargs):
    instance.create_permissions()


@receiver(pre_delete, sender=CkfinderResource)
def delete_auth(sender, instance, **kwargs):
    instance.delete_permissions()
