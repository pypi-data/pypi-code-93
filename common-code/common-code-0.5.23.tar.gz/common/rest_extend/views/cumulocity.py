from django.db import transaction
from common.rest_extend.response import Results, SUCCESS, get_error_status_code, RESTResponse
from common.rest_extend.views.related import RelatedView


class SynchronousError(Exception):
    pass


class CumulocityView(RelatedView):
    def post(
        self,
        request,
        obj,
        obj_serializer,
        data=None,
        need_results=False,
        related_obj: list = None,
        m_to_m_obj: list = None,
        related_mapping=None,
        m_to_m_mapping=None,
        **kwargs,
    ):
        results = Results()
        try:
            with transaction.atomic():
                results = Results()
                if not data:
                    data = request.data
                if data.get("data"):
                    data = data.get("data")
                success = self.execute_cumulocity(request, results, data)
                if not success:
                    return RESTResponse(results)
                serializer = obj_serializer(data=data)
                if not related_obj:
                    related_obj, related_mapping = self.injection_related_data("POST")
                if not m_to_m_obj:
                    m_to_m_obj, m_to_m_mapping = self.injection_m_to_m_data("POST")
                self.execute_related_extend(related_obj, related_mapping, data)
                self.execute_m_to_m_extend(m_to_m_obj, m_to_m_mapping, data)
                try:
                    valid = serializer.is_valid(raise_exception=True)
                    serializer.save()
                    results.describe = "add  successfully！！！"
                    results.code = 200
                except Exception as e:
                    results.code, results.describe = get_error_status_code(e)
                self.post_transaction(request, results)
        except SynchronousError as e:
            pass
        except Exception as e:
            get_error_status_code(e, results)
        return RESTResponse(results)

    def put(
        self,
        request,
        obj,
        obj_serializer,
        data=None,
        pk="id",
        extend_conditions: dict = None,
        need_results=False,
        need_queryset=False,
        **kwargs,
    ):
        results = Results()
        try:
            with transaction.atomic():
                response = super().put(
                    request,
                    obj,
                    obj_serializer,
                    data=data,
                    pk=pk,
                    extend_conditions=extend_conditions,
                    need_results=need_results,
                    need_queryset=need_queryset,
                    **kwargs,
                )
                self.put_transaction(request, results)
            return response
        except SynchronousError as e:
            pass
        except Exception as e:
            get_error_status_code(e, results)
        return RESTResponse(results)

    def delete(
        self,
        request,
        obj,
        obj_serializer,
        data=None,
        pk="id",
        extend_conditions: dict = None,
        need_results=False,
        need_queryset=False,
        **kwargs,
    ):
        results = Results()
        try:
            with transaction.atomic():
                results, instance = super().delete(
                    request,
                    obj=obj,
                    obj_serializer=obj_serializer,
                    data=data,
                    pk=pk,
                    extend_conditions=extend_conditions,
                    need_queryset=True,
                    **kwargs,
                )
                if instance:
                    self.delete_transaction(request, results, instance=instance)
        except SynchronousError as e:
            pass
        except Exception as e:
            get_error_status_code(e, results)
        return RESTResponse(results)

    def post_transaction(self, request, results, **kwargs):
        pass

    def put_transaction(self, request, results, **kwargs):
        pass

    def delete_transaction(self, request, results, **kwargs):
        pass

    def injection_post_data(self, data, **kwargs):

        pass

    def execute_cumulocity(self, request, results, data, **kwargs):
        return True
