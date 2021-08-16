# -*- coding: utf-8 -*-
# @Time: 2020-06-02 10:10:03.714421


from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema

from framework.filters import MyFilterBackend, MyFilterSerializer, OrderingFilter
from framework.route import Route
from framework.serializer import BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, ListIntField, \
    ListStrField, PaginationSerializer, s
from framework.views import action, action_post, CurdViewSet, JsonResponse, render_to_response, RspError
from myadmin.models import Role
from ..models.resource import Resource


class RoleSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/
    # resource = s.PrimaryKeyRelatedField(many=True,label=_("资源对象"),queryset=Role.resource.field.related_model.objects.all() )
    resource_map_ids = s.DictField(child=s.ListField(), required=False, help_text=_('角色资源列表'), read_only=True)
    type_alias = s.CharField(required=False, read_only=True)
    creater_alias = s.CharField(source='creater.alias', required=False, read_only=True)
    parent_alias = s.CharField(source='parent.alias', required=False, read_only=True)

    menu = ListStrField(label=_('菜单ID'), write_only=True, required=False)
    role = ListIntField(label=_('管理角色ID'), write_only=True, required=False)

    user = ListIntField(label=_('成员'), write_only=True, required=False)

    class Meta:
        model = Role
        fields = ['id', 'alias', 'name', 'parent', 'creater_alias', 'parent_alias', 'resource_map_ids', 'type',
                  'type_alias', 'remark',
                  'home_index', 'create_datetime', 'update_datetime', 'user'] \
                 + ['menu', 'role']
        # exclude = ['session_key']
        # read_only_fields = []
        # write_only_fields=['creater']


class ListRoleRspSerializer(PaginationSerializer):
    results = RoleSerializer(many=True)


@Route('myadmin/role')
class RoleSet(CurdViewSet):
    filter_backends = (MyFilterBackend, OrderingFilter)

    serializer_class = RoleSerializer
    # 可条件过滤的字段
    filter_fields = ['id', 'alias', 'name', 'parent', 'type', 'remark', 'home_index', 'create_datetime',
                     'update_datetime']
    # 可排序的字段
    ordering_fields = ['id', 'alias', 'name', 'parent', 'type', 'remark', 'home_index', 'create_datetime',
                       'update_datetime']

    model = Role

    def get_queryset(self):
        return self.request.user.get_resource('role').prefetch_related(*['resource']).select_related(
                *['parent', 'creater'])

    @swagger_auto_schema(query_serializer=MyFilterSerializer, responses=ListRoleRspSerializer)
    def list(self, request, *args, **kwargs):
        """角色列表"""
        return render_to_response("myadmin/role/list.html", super().list(request, *args, **kwargs))

    class RoleEditParmas(EditParams):
        type = s.IntegerField(label=_('类型'), required=False)
        parent = s.IntegerField(label=_('父节点'), required=False)

    @swagger_auto_schema(query_serializer=EditParams, responses=RoleSerializer)
    def edit(self, request, *args, **kwargs):
        """角色编辑"""
        model_instance: Role = self.get_model_instance(EditParams)
        params = self.RoleEditParmas(request.query_params).params_data
        if not model_instance.id:
            if params.type:
                model_instance.type = params.type
            if params.parent and int(params.parent) != model_instance.id:
                model_instance.parent = Role.objects.get(id=params.parent)
        serializer = self.get_serializer(instance=model_instance)
        return render_to_response("myadmin/role/edit.html", self.response(serializer.data))

    class RoleSaveError(RspError):
        pass

    @swagger_auto_schema(query_serializer=IdSerializer, request_body=RoleSerializer, responses=RoleSerializer)
    def save(self, request, *args, **kwargs):
        """角色保存"""
        role = self.get_model_instance(IdSerializer)

        if not request.user.is_manager:
            raise self.RoleSaveError(_('只有管理员才能添加角色!'))
        if not role.id:
            role.creater = request.user
        serializer, msg = self.save_instance(request, role)
        role = serializer.instance
        params: RoleSerializer = serializer.params_data
        manager_role_ids = params.role  # 只有管理员才能管理其他角色

        for rsource_name, model_resource in Resource.get_resource_map().items():
            if not model_resource.is_inner:
                role.create_resource(rsource_name, request.data.get(model_resource.id_field_lookup, []))

        role.create_resource('menu', params.menu or [])
        role.create_resource('role', manager_role_ids or [])
        if request.user.is_root:
            role.create_resource('user', params.user or [])

        return self.response(serializer.data, msg=msg)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request, *args, **kwargs):
        """角色删除"""
        return super(RoleSet, self).delete(request, *args, **kwargs)

    class RoleResourceMembersSer(IdSerializer):
        members = s.DictField(child=s.ListField(), required=False, help_text=_('角色资源列表'), read_only=True)

    @swagger_auto_schema(methods=['get'], query_serializer=IdSerializer, responses=RoleResourceMembersSer)
    @action(['get'])
    def resource_members(self, request):
        """
        获取 角色下的成员
        :param request:
        :return:
        """
        parmas = self.RoleResourceMembersSer(request.query_params).params_data

        if parmas.id:
            role_model = self.get_queryset().filter(id=parmas.id).first()
            if role_model:
                parmas.members = role_model.resource_map_ids
        return JsonResponse(parmas)

    @swagger_auto_schema(query_serializer=EditParams, responses=RoleSerializer)
    @action_post()
    def update(self, request):
        """更新角色信息"""
        model: Role = self.get_model_instance()

        serializer, msg = self.save_instance(request, model)
        return self.response(serializer, msg=msg)
