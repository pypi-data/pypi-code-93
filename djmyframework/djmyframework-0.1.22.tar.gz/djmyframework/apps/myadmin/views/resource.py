# -*- coding: utf-8 -*-
# @Time: 2020-06-12 11:43:24.296293


from drf_yasg.utils import swagger_auto_schema
from framework.filters import MyFilterBackend, OrderingFilter, MyFilterSerializer
from django.utils.translation import gettext_lazy as _
from framework.route import Route
from framework.serializer import s,BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, ParamsSerializer, PaginationSerializer
from framework.views import CurdViewSet, ListPageNumberPagination, Response,action
from myadmin.models import Resource


class ResourceSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/


    class Meta:
        model = Resource
        fields =  ['id', 'name', 'role_id', 'create_datetime', 'update_datetime'] or '__all__'
        #exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']



class ListResourceRspSerializer(PaginationSerializer):
    results = ResourceSerializer(many=True)

@Route('myadmin/resource')
class ResourceSet(CurdViewSet):
    filter_backends = (MyFilterBackend,OrderingFilter)

    serializer_class = ResourceSerializer
    # 可条件过滤的字段
    filter_fields =  ['id', 'name', 'role_id', 'create_datetime', 'update_datetime']
    # 可排序的字段
    ordering_fields = ['id', 'name', 'role_id', 'create_datetime', 'update_datetime']

    model = Resource

    def get_queryset(self):
        return Resource.objects.all().prefetch_related(*[]).select_related(*[])

    @swagger_auto_schema(query_serializer=MyFilterSerializer,responses=ListResourceRspSerializer)
    def list(self, request, *args, **kwargs):
        """资源 列表"""
        return super(ResourceSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(query_serializer=EditParams, responses=ResourceSerializer)
    def edit(self, request, *args, **kwargs):
        """资源 编辑"""
        return super(ResourceSet, self).edit(request, *args, **kwargs)

    @swagger_auto_schema(query_serializer=IdSerializer,request_body=ResourceSerializer, responses=ResourceSerializer)
    def save(self, request, *args, **kwargs):
        """资源 保存"""
        return super(ResourceSet, self).save(request, *args, **kwargs)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request, *args, **kwargs):
        return super(ResourceSet, self).delete(request, *args, **kwargs)


    # @swagger_auto_schema(methods=['post'], request_body=ResourceSerializer, responses=ResourceSerializer)
    # @action(['post'])
    # def foo_action(self, request):
    #     return Response(ResourceSerializer().data)