"""
admin.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/2/21 10:53 AM
"""
from django.conf import settings
from django.contrib.auth import get_permission_codename
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse, NoReverseMatch
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import ModelAdmin, site

from . import models


class CkfinderResource(ModelAdmin):
    """
    Ckfinder 资源
    """

    list_display = (
        'pk',
        'adapter',
        'name',
        'max_size',
        'path',
        'url',
        'allowed_extensions',
        'denied_extensions',
        'enabled',
        'verify_permissions',
    )
    list_display_links = ('pk', 'adapter')
    list_editable = ('name', 'max_size', 'enabled', 'verify_permissions')
    list_filter = ('adapter', 'enabled', 'verify_permissions')
    search_fields = ('name', 'adapter')

    fieldsets = (
        (_('基础配置'), {
            'fields': (
                'adapter',
                'name',
                'path',
                'url',
                'enabled',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('上传限制'), {
            'fields': (
                'allowed_extensions',
                'denied_extensions',
                'max_size',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('权限管理'), {
            'fields': (
                'verify_permissions',
                'ck_finder_file_create',
                'ck_finder_file_delete',
                'ck_finder_file_rename',
                'ck_finder_file_view',
                'ck_finder_folder_create',
                'ck_finder_folder_delete',
                'ck_finder_folder_rename',
                'ck_finder_folder_view',
                'ck_finder_image_resize',
                'ck_finder_image_resize_custom',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('其他配置'), {
            'fields': (
                'other',
            ),
            'classes': ('extrapretty', 'wide')
        }),
    )

    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        if 'action_list' in list_display:
            list_display.remove('action_list')
        if self.has_ckfinder_manage_permission(request=request):
            list_display.append('action_list')
        return list_display

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super().get_urls()
        urls = [
                   path('ckfinder/', self.ckfinder_view, name='%s_%s_ckfinder' % info)
               ] + urls
        return urls

    def ckfinder_view(self, request, **kwargs):
        """
        ckfinder 管理页面
        :param request:
        :param kwargs:
        :return:
        """
        if not request.user.is_authenticated:
            try:
                login_url = reverse(settings.LOGIN_URL)
            except NoReverseMatch:
                login_url = reverse('admin:login')
            return HttpResponseRedirect(login_url)
        if not self.has_ckfinder_manage_permission(request):
            raise PermissionDenied

        return render(request=request, template_name='kelove_database/ckfinder/ckfinder.html', context={
            "ck_finder_api_url": reverse('django_kelove_database:ckfinder_api'),
            "ck_finder_api_display_folders_panel": 0
        })

    def has_ckfinder_manage_permission(self, request):
        """
        判断是否有管理权限
        """
        opts = self.opts
        codename = get_permission_codename('manage', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def action_list(self, obj):
        return mark_safe('<a href="{url}" target="_blank">{title}</a>'.format(
            url=reverse('admin:django_kelove_database_ckfinderresource_ckfinder'),
            title='管理'
        ))

    action_list.short_description = '操作'


if not site.is_registered(models.CkfinderResource):
    site.register(models.CkfinderResource, CkfinderResource)
