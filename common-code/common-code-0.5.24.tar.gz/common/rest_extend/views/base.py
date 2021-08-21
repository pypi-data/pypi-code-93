

class BaseView2(APIView, Select):
    """
    对实体模型增删改查的父类
    """

    def get(self, request, obj, obj_serializer, data=None, need_results=False, need_queryset=False, keys=None):
        """
        根据键值对查找数据
        :param request:
        :param obj:
        :param obj_serializer:
        :param data:
        :param need_results:
        :param keys:
        :return:
        """
        if not data:
            data = request.GET
        results, queryset, current_page_queryset = self.find(obj, data, obj_serializer)
        if need_results:
            return results
        if need_queryset:
            return results, queryset
        return RESTResponse(results)

    def post(self, request, obj, obj_serializer, data=None, need_results=False, **kwargs):
        """
        添加数据
        :param request:
        :param obj:
        :param obj_serializer:
        :param data:
        :param need_results:
        :return:
        """
        results = Results()
        if not data:
            data = request.data
        if data.get("data"):
            data = data.get("data")
        serializer = obj_serializer(data=data)
        try:
            valid = serializer.is_valid(raise_exception=True)
            serializer.save()
            results.describe = "add  successfully！！！"
            results.status = SUCCESS
            results.code = 200
        except Exception as e:
            results.code, results.describe = get_error_status_code(e)

        if need_results:
            return results
        return RESTResponse(results)

    def put(self, request, obj, obj_serializer, data=None, need_results=False, pk="id", **kwargs):
        """
        根据主键，或某个字段更新数据
        :param request:
        :param obj:
        :param obj_serializer:
        :param data:
        :param need_results:
        :param pk:
        :return:
        """
        results = Results()
        results.code = 200
        if not data:
            data = request.data
        if data.get("data"):
            data = data.get("data")
        partial = True
        if request.GET.get("pk"):
            pk = request.GET.get("pk")
        try:
            value_pk = data.get(pk)
            if not value_pk:
                results.describe = "'pk' cannot be empty"
                results.code = REQUEST_ERROR_CODE

            else:
                if pk == "id":
                    try:
                        value_pk = int(value_pk)
                    except:
                        raise ValidationError("'pk' type error Should be <int>！！！")

                instance = obj.objects.filter(**{pk: value_pk}).first()
                if not instance:
                    results.describe = pk + "=" + str(value_pk) + "  does not exist"
                    results.code = REQUEST_ERROR_CODE
                else:

                    serializer = obj_serializer(instance, data=data, partial=partial)
                    try:
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        results.describe = "update  successfully！！！"
                        results.status = SUCCESS
                    except Exception as e:
                        results.code, results.describe = get_error_status_code(e)
                    if getattr(instance, "_prefetched_objects_cache", None):
                        # If 'prefetch_related' has been applied to a queryset, we need to
                        # forcibly invalidate the prefetch cache on the instance.
                        instance._prefetched_objects_cache = {}

        except Exception as e:
            results.code, results.describe = get_error_status_code(e)

        if need_results:
            return results
        return RESTResponse(results)

    def delete(self, request, obj, obj_serializer, data=None, need_results=False, pk="id", **kwargs):
        """
        根据主键删除数据
        :param request:
        :param obj:
        :param obj_serializer:
        :param data:
        :param need_results:
        :param pk:
        :return:
        """
        results = Results()
        results.code = 200
        if not data:
            data = request.data
        if data.get("data"):
            data = data.get("data")
        if request.GET.get("pk"):
            pk = request.GET.get("pk")
        value_pk = data.get(pk)
        if not value_pk:
            results.describe = "'pk' cannot be empty"
            results.code = REQUEST_ERROR_CODE
        else:
            try:
                if pk == "id":
                    try:
                        value_pk = int(value_pk)
                    except:
                        raise ValidationError("'pk' type error Should be <int>！！！")

                instance = obj.objects.filter(**{pk: value_pk}).first()
                if not instance:
                    results.describe = pk + "=" + str(value_pk) + " does not exist"
                    results.code = REQUEST_ERROR_CODE
                else:
                    instance.delete()
                    results.describe = "deleted successfully！！！"
                    results.status = SUCCESS
            except Exception as e:
                results.code, results.describe = get_error_status_code(e)

        if need_results:
            return results
        return RESTResponse(results)

    def get_queryset(self, obj, data) -> (QuerySet, QuerySet):
        return super(BaseView, self).get_queryset(obj, data)

