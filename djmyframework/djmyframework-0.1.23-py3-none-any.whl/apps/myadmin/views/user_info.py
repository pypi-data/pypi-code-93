# -*- coding: utf-8 -*-
# @Time: 2020-06-11 12:36:55.596678


from drf_yasg.utils import swagger_auto_schema
from framework.filters import MyFilterBackend, OrderingFilter, MyFilterSerializer
from django.utils.translation import gettext_lazy as _
from framework.route import Route
from framework.serializer import s, BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, ParamsSerializer, \
    PaginationSerializer
from framework.views import CurdViewSet, ListPageNumberPagination, Response, action, notcheck
from myadmin.models import UserInfo, User


class UserInfoSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/


    class Meta:
        model = UserInfo
        fields = ['id', 'user', 'user_alias', 'employee_id', 'sex', 'email', 'email_active', 'qq', 'phone',
                  'phone_active', 'create_datetime', 'update_datetime'] or '__all__'
        # exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']


class ListUserInfoRspSerializer(PaginationSerializer):
    results = UserInfoSerializer(many=True)


@Route('myadmin/user_info')
class UserInfoSet(CurdViewSet):
    filter_backends = (MyFilterBackend, OrderingFilter)

    serializer_class = UserInfoSerializer
    # 可条件过滤的字段
    filter_fields = ['id', 'user', 'employee_id', 'sex', 'email', 'email_active', 'qq', 'phone', 'phone_active',
                     'create_datetime', 'update_datetime']
    # 可排序的字段
    ordering_fields = ['id', 'user', 'employee_id', 'sex', 'email', 'email_active', 'qq', 'phone', 'phone_active',
                       'create_datetime', 'update_datetime']

    model = UserInfo

    def get_queryset(self):
        return UserInfo.objects.all().prefetch_related(*[]).select_related(*['user'])

    @swagger_auto_schema(query_serializer=MyFilterSerializer, responses=ListUserInfoRspSerializer)
    def list(self, request, *args, **kwargs):
        """
        个人信息 列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return super(UserInfoSet, self).list(request, *args, **kwargs)

    class UserInfoEditParmas(EditParams):
        user_id = s.IntegerField(label=_('管理员id'), required=False)

    @swagger_auto_schema(query_serializer=UserInfoEditParmas, responses=UserInfoSerializer)
    def edit(self, request, *args, **kwargs):
        model_instance = self.get_model_instance()
        parmas = self.UserInfoEditParmas(request.query_params).params_data
        if parmas.user_id:
            model_instance,_c = UserInfo.objects.get_or_create(user=User.objects.get(id=parmas.user_id))
        serializer = self.get_serializer(instance=model_instance)
        return self.response(serializer.data)

    @swagger_auto_schema(query_serializer=UserInfoEditParmas, responses=UserInfoSerializer)
    @action()
    @notcheck
    def edit_self(self, request, *args, **kwargs):
        """
        编辑个人信息
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        model_instance, c = UserInfo.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(instance=model_instance)
        return self.response(serializer.data)

    @swagger_auto_schema(query_serializer=IdSerializer, request_body=UserInfoSerializer, responses=UserInfoSerializer)
    @action('post')
    @notcheck
    def save_self(self, request, *args, **kwargs):
        """
        个人信息保存
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return super(UserInfoSet, self).save(request, *args, **kwargs)

    @swagger_auto_schema(query_serializer=IdSerializer, request_body=UserInfoSerializer, responses=UserInfoSerializer)
    def save(self, request, *args, **kwargs):
        """个人信息 保存"""
        return super(UserInfoSet, self).save(request, *args, **kwargs)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request, *args, **kwargs):
        """个人信息 删除"""
        return super(UserInfoSet, self).delete(request, *args, **kwargs)




    # @swagger_auto_schema(methods=['post'], request_body=UserInfoSerializer, responses=UserInfoSerializer)
    # @action(['post'])
    # def foo_action(self, request):
    #     return Response(UserInfoSerializer().data)