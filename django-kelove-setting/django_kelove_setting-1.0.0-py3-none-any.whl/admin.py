"""
admin.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/24/21 11:29 AM
"""

from collections.abc import Iterable

from django.utils.translation import gettext_lazy as _
from django.contrib.admin import ModelAdmin, site
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.apps import apps
from django.conf import settings

from . import KELOVE_SETTINGS_APP_KEY
from .models import Settings as SettingsModel
from .utils import get_settings_form_class

try:
    from import_export.admin import ImportExportMixin
    from import_export.resources import ModelResource
    from import_export.fields import Field
    from import_export.widgets import JSONWidget, CharWidget


    class SettingsImportExportResource(ModelResource):
        """
        配置导入导出处理类
        """

        settings_key = Field(
            column_name=_('配置标识'),
            attribute='settings_key',
            default='',
            saves_null_values=False,
            widget=CharWidget()
        )

        settings_title = Field(
            column_name=_('配置名称'),
            attribute='settings_title',
            default='',
            saves_null_values=False,
            widget=CharWidget()
        )

        settings_val = Field(
            column_name=_('配置内容'),
            attribute='settings_val',
            saves_null_values=False,
            widget=JSONWidget()
        )

        class Meta:
            fields = ['settings_key', 'settings_title', 'settings_val']
            import_id_fields = ['settings_key']
            use_transactions = True
            model = SettingsModel


    class BaseSettingsModelAdmin(ImportExportMixin, ModelAdmin):
        resource_class = SettingsImportExportResource
except ModuleNotFoundError:
    class BaseSettingsModelAdmin(ModelAdmin):
        pass


class SettingsModelAdmin(BaseSettingsModelAdmin):
    """
    配置管理
    """

    change_form_template = 'kelove_setting/change_form.html'

    list_display = (
        'id',
        'settings_title',
        'settings_key',
        'created_user',
        'created_time',
        'updated_user',
        'updated_time',
    )

    list_display_links = ('settings_title', 'settings_key')

    list_filter = ('created_time', 'updated_time')

    search_fields = ('settings_title', 'settings_key')

    readonly_fields = ('settings_title', 'settings_key')

    def get_fieldsets(self, request, obj=None):
        """
        Hook for specifying fieldsets.
        :param request:
        :param obj:
        :return:
        """
        form = self.get_form(request=request, obj=obj)
        if form.fieldsets:
            return form.fieldsets
        fieldsets = form.get_fieldsets(model_admin=self, request=request, obj=obj)
        if fieldsets:
            return fieldsets
        return super().get_fieldsets(request=request, obj=obj)

    def has_change_permission(self, request, obj=None):
        if not obj:
            return super().has_change_permission(request, obj)
        return request.user.has_perm(obj.get_settings_permission_code('change'))

    def has_delete_permission(self, request, obj=None):
        if not obj:
            return super().has_delete_permission(request, obj)
        return request.user.has_perm(obj.get_settings_permission_code('delete'))

    def has_view_permission(self, request, obj=None):
        if not obj:
            return super().has_view_permission(request, obj)
        return (
                request.user.has_perm(obj.get_settings_permission_code('change')) or
                request.user.has_perm(obj.get_settings_permission_code('view'))
        )

    def add_view(self, request, form_url='', extra_context=None):
        """
        初始化配置表
        :param request:
        :param form_url:
        :param extra_context:
        :return:
        """

        app_configs = apps.get_app_configs()
        kelove_settings = [
            j
            for i in app_configs
            for j in getattr(i, KELOVE_SETTINGS_APP_KEY, [])
            if
            hasattr(i, KELOVE_SETTINGS_APP_KEY)
            and isinstance(getattr(i, KELOVE_SETTINGS_APP_KEY, []), Iterable)
            and not isinstance(getattr(i, KELOVE_SETTINGS_APP_KEY, []), str)
        ]
        kelove_settings += [i for i in getattr(settings, 'KELOVE_SETTINGS_CLASSES', [])]
        kelove_settings = set(kelove_settings)

        for form in kelove_settings:
            # 获取配置表单类
            form = get_settings_form_class(form_class=form)
            if not form:
                continue

            # 初始化
            obj, is_create = SettingsModel.objects.get_or_create(settings_key=form.get_settings_key())
            obj.settings_title = form.get_settings_title(is_full=False)
            obj.settings_val = form.get()
            obj.created_user = obj.updated_user = request.user
            obj.save()

            # 创建权限
            obj.create_admin_settings_auth()
            # 清理缓存
            form.delete_cache()

        opts = self.model._meta
        obj_url = reverse(
            'admin:%s_%s_changelist' % (opts.app_label, opts.model_name),
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(obj_url)

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj:
            return get_settings_form_class(form_class=obj.settings_key)
        return super().get_form(request, obj, change, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        自动写入创建用户ID和更新用户ID
        :param request:
        :param obj:
        :param form:
        :param change:
        :return:
        """

        if request.user:
            user = request.user
            obj.updated_user = user
            if not change:
                obj.created_user = user
        super().save_model(request, obj, form, change)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        title = context.get('title', '')
        sub_title = getattr(obj, 'settings_title', '')
        if sub_title and title:
            context['title'] = f'{title} - {sub_title}'
        return super().render_change_form(request, context, add, change, form_url, obj)

    def get_queryset(self, request):
        all_view_permissions = self.__get_all_permissions(request, 'view')
        qs = super().get_queryset(request)
        qs = qs.filter(
            settings_key__in=all_view_permissions
        ).select_related('created_user', 'updated_user')
        return qs

    @staticmethod
    def __get_all_permissions(request, permission_type='view'):
        settings_items = SettingsModel.objects.all()
        permissions = [
            i.settings_key
            for i
            in settings_items
            if request.user.has_perm(i.get_settings_permission_code(permission_type))
        ]
        return permissions


if not site.is_registered(SettingsModel):
    site.register(SettingsModel, SettingsModelAdmin)
