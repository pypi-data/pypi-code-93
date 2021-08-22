from common.rest_extend.decorator import tenant_decorator

from common.rest_extend.views.views import BaseView


class IntegrateView(BaseView):
    @tenant_decorator
    def get(
            self,
            request,
            obj,
            obj_serializer,
            *,
            data=None,
            extend_conditions: dict = None,
            need_results=False,
            need_queryset=False,
            keys=None,
            **kwargs,
    ):
        return super(IntegrateView, self).get(
            request,
            obj,
            obj_serializer,
            data=data,
            extend_conditions=extend_conditions,
            need_results=need_results,
            need_queryset=need_queryset,
            keys=keys,
            **kwargs,
        )

    @tenant_decorator
    def post(self, request, obj, obj_serializer, *, data=None, need_results=False, **kwargs):
        return super(IntegrateView, self).post(
            request, obj, obj_serializer, data=data, need_results=need_results, **kwargs
        )

    @tenant_decorator
    def put(
            self,
            request,
            obj,
            obj_serializer,
            *,
            data=None,
            pk="id",
            extend_conditions: dict = None,
            need_results=False,
            **kwargs,
    ):
        return super(IntegrateView, self).put(
            request,
            obj,
            obj_serializer,
            data=data,
            pk=pk,
            extend_conditions=extend_conditions,
            need_results=need_results,
            **kwargs,
        )

    @tenant_decorator
    def delete(
            self,
            request,
            obj,
            obj_serializer,
            *,
            data=None,
            pk="id",
            extend_conditions: dict = None,
            need_results=False,
            **kwargs,
    ):
        return super(IntegrateView, self).delete(
            request,
            obj,
            obj_serializer,
            data=data,
            pk=pk,
            extend_conditions=extend_conditions,
            need_results=need_results,
            **kwargs,
        )
