# -*- coding: utf-8 -*-
# @Time: 2020-06-16 09:19:23.389973


from drf_yasg.utils import swagger_auto_schema

from framework.filters import MyFilterBackend, MyFilterSerializer, OrderingFilter
from framework.route import Route
from framework.serializer import BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, PaginationSerializer, s
from framework.views import action, CurdViewSet, JsonResponse, notcheck, Request
from log_def.models import DictDefine


class DictDefineSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/
    type_alias = s.CharField(source='get_type_display', required=False, read_only=True)

    class Meta:
        model = DictDefine
        fields = ['id', 'name', 'key', 'group', 'json_dict', 'type', 'remark', 'create_datetime', 'update_datetime',
                  'type_alias'] or '__all__'
        # exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']


class ListDictDefineRspSerializer(PaginationSerializer):
    results = DictDefineSerializer(many=True)


@Route('log_def/dict_define')
class DictDefineSet(CurdViewSet):
    filter_backends = (MyFilterBackend, OrderingFilter)
    serializer_class = DictDefineSerializer
    # 可条件过滤的字段
    filter_fields = ['id', 'name', 'key', 'group', 'type', 'remark', 'create_datetime', 'update_datetime']
    # 可排序的字段
    ordering_fields = ['id', 'name', 'key', 'group', 'type', 'remark', 'create_datetime', 'update_datetime']

    model = DictDefine

    def get_queryset(self):
        return DictDefine.objects.all().prefetch_related(*[]).select_related(*[])

    @swagger_auto_schema(query_serializer=MyFilterSerializer, responses=ListDictDefineRspSerializer)
    def list(self, request, *args, **kwargs):
        """字典定义 列表"""
        return super(DictDefineSet, self).list(request, *args, **kwargs)

    class DictDefineEditParmas(EditParams):
        key = s.CharField(required=False)

    @swagger_auto_schema(query_serializer=EditParams, responses=DictDefineSerializer)
    def edit(self, request, *args, **kwargs):
        """字典定义 编辑"""
        model_instance = self.get_model_instance(EditParams)
        params = self.DictDefineEditParmas(request.query_params).params_data
        if params.key:
            model_instance = DictDefine.objects.filter(key=params.key).first() or DictDefine()
            model_instance.key = params.key
        serializer = self.get_serializer(instance=model_instance)
        return self.response(serializer.data)

    @swagger_auto_schema(query_serializer=IdSerializer, request_body=DictDefineSerializer,
                         responses=DictDefineSerializer)
    def save(self, request, *args, **kwargs):
        """字典定义 保存"""

        model_instance: DictDefine = self.get_model_instance(IdSerializer)
        model_instance.json_dict = request.data.get('dict', {})
        serializer, msg = self.save_instance(request)
        return self.response(serializer.data, msg=msg)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request, *args, **kwargs):
        return super(DictDefineSet, self).delete(request, *args, **kwargs)

    @notcheck
    @action('get')
    def interface(self, request: Request, *args, **kwargs):
        '''获取字典的接口
        '''

        key = request.query_params.get('key')
        _r = {}
        if key:
            o = DictDefine.objects.filter(key=key).first()
            if o:
                _r = o.get_dict()
        return JsonResponse(_r)
