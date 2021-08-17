from dataclasses import asdict

from django.http import JsonResponse

from common.rest_extend.response import Results, get_error_status_code, RESTResponse


def vaild_decorator(obj=None, obj_serializer=None, partial=False):
    """
    参数验证装饰器（这里当 middleware ，验证失败不往下执行，直接返回Response）
    :param obj: 实体类
    :param obj_serializer: 需要校验的序列化类
    :param partial: 是否部分校验
    :return:
    """

    def external_wrapper(function):
        def internal_wrapper(obj_request, request, *args, **kwargs):
            """

            :param obj_request: 被装饰的实体类
            :param request:
            :param args:
            :param kwargs:
            :return:
            """
            try:
                if request.method == "GET":
                    data = request.GET
                else:
                    data = request.data
                serializer = obj_serializer(data=data, partial=partial)
                valid = serializer.is_valid(raise_exception=True)
                kwargs["obj_ser"] = serializer
            except Exception as e:
                results = Results()
                results.describe = str(e)
                status_code, describe = get_error_status_code(e)
                return RESTResponse(asdict(results), status=status_code)
            return function(obj_request, request, *args, **kwargs)
            # response = function(obj_request, request, *args, **kwargs)
            # if json.loads(response.content).get('status') != SUCCESS:
            #     response.status = SERVER_ERROR_CODE
            # return response

        return internal_wrapper

    return external_wrapper


def view_decorator(function):
    """
    视图装饰器
    :param function:
    :return:
    """

    def wrapper(request, *args, **kwargs):
        return function(request, *args, **kwargs)

    return wrapper


def relevance_vaild_legal_decorator(func):
    def wrapper(request, *args, **kwargs):
        # if request.method != "GET" and request.method != "POST":
        #     return JsonResponse({"detail": f'Method "{request.method}" not allowed.'}, status=405)
        group = request.GET.get("group")
        if group:
            results = Results()
            results.describe = "此接口不支持参数 'group'！！！"
            return RESTResponse(results)
        return func(request, *args, **kwargs)

    return wrapper
