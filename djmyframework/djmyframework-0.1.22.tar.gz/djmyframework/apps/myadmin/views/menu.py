# -*- coding: utf-8 -*-
# @Time: 2020-06-02 17:00:36.748370


from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema

from framework.filters import MyFilterBackend, MyFilterSerializer, OrderingFilter
from framework.route import Route
from framework.serializer import BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, PaginationSerializer, s
from framework.views import action_get_post, CurdViewSet, notcheck, render_to_response, Request
from myadmin.models import Menu, MenuConfig



class MenuSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/
    label = s.CharField(label=_('已翻译名'), read_only=True)

    # def get_label(self, model: Menu):
    #     return _(model.alias)

    # def validate_alias(self, value):
    #     if not self.instance.id:
    #         if Menu.objects.filter(alias=value).exists():
    #             raise s.ValidationError('%s 已存在'% value)
    #     return value

    class Meta:
        model = Menu
        fields = ['id', 'parent_id', 'label', 'alias', 'name', 'url', 'icon', 'css', 'order', 'is_show', 'is_log',
                  'create_datetime'] or '__all__'
        # exclude = ['session_key']
        read_only_fields = ['update_datetime', 'create_datetime']


class ListMenuRspSerializer(PaginationSerializer):
    results = MenuSerializer(many=True)


@Route('myadmin/menu')
class MenuSet(CurdViewSet):
    filter_backends = (MyFilterBackend, OrderingFilter)

    serializer_class = MenuSerializer
    # 可条件过滤的字段
    filter_fields = ['id', 'parent_id', 'alias', 'name', 'url', 'url_path', 'icon', 'css', 'order', 'is_show', 'is_log',
                     'create_datetime', 'update_datetime']
    # 可排序的字段
    ordering_fields = ['id', 'parent_id', 'alias', 'name', 'url', 'url_path', 'icon', 'css', 'order', 'is_show',
                       'is_log', 'create_datetime', 'update_datetime']

    model = Menu

    def get_queryset(self):
        return self.request.user.get_resource('menu').all().order_by('parent_id', 'order', 'id').prefetch_related(
                *[]).select_related(
                *[])

    @swagger_auto_schema(query_serializer=MyFilterSerializer, responses=ListMenuRspSerializer)
    @notcheck
    def list(self, request, *args, **kwargs):
        """菜单管理"""
        return super(MenuSet, self).list(request, *args, **kwargs)

    class EditMenuParams(EditParams):
        parent_id = s.IntegerField(label=_('父节点ID'), required=False)

    @swagger_auto_schema(query_serializer=EditMenuParams, responses=MenuSerializer)
    def edit(self, request, *args, **kwargs):
        """菜单编辑"""
        params = self.EditMenuParams(request.query_params).params_data
        model: Menu = self.get_model_instance(self.EditMenuParams)
        if not model.id and params.parent_id:
            model.parent_id = params.parent_id
        serializer = self.get_serializer(model)
        return render_to_response('myadmin/menu/edit.html', serializer)

    @swagger_auto_schema(query_serializer=IdSerializer, request_body=MenuSerializer, responses=MenuSerializer)
    def save(self, request, *args, **kwargs):
        """菜单保存"""
        return render_to_response('myadmin/menu/list.html', super().save(request))

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request, *args, **kwargs):
        """菜单删除"""
        return super(MenuSet, self).delete(request, *args, **kwargs)

    @action_get_post
    def update_menu(self, request: Request):
        """
        更新菜单
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        install_app_menu_config_list = MenuConfig.get_install_app_menu_config_list()

        created_menu_name_list = set(list(Menu.objects.values_list('name', flat=True)))
        to_be_added_menu_list = [mc for mc in install_app_menu_config_list if (not mc.name in created_menu_name_list) and mc.name]
        msg = ''
        if self.is_post():
            add_menus = request.data.getlist('menu',[])
            if add_menus:
                MenuConfig.create_menu_from_config(install_app_menu_config_list, add_menus=add_menus)
            msg = 'Create %s menu OK' % len(add_menus)

        return render_to_response('myadmin/menu/update_menu.html', locals(), msg=msg)

    # @swagger_auto_schema(methods=['post'], request_body=MenuSerializer, responses=MenuSerializer)
    # @action(['post'])
    # def foo_action(self, request):
    #     return Response(MenuSerializer().data)
