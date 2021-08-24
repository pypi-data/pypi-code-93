"""
views.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/2/21 11:18 AM
"""
from inspect import isfunction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .ckfinder.ckfinder import Ckfinder
from .ckfinder.util import load_object
from .models import CkfinderResource
from .kelove_settings import CkfinderFieldSettings


def ckfinder(request):
    return render(request, 'kelove_database/ckfinder/ckfinder.html', {
        "ck_finder_api_url": reverse('django_kelove_database:ckfinder_api'),
        "ck_finder_api_display_folders_panel": 0
    })


def __get_response(response_data):
    if response_data['content_type'].lower() == 'application/json':
        response = JsonResponse(data=response_data['content'])
    else:
        response = HttpResponse(
            content=response_data['content'],
            content_type=response_data['content_type'],
        )
    response.status_code = response_data['status_code']

    for header_key, header_val in response_data['headers'].items():
        response[header_key] = header_val
    return response


def __get_file(request):
    file = {}
    file_obj = request.FILES.get('upload', None)
    if file_obj:
        file['name'] = file_obj.name
        file['file'] = file_obj.file
    return file


@csrf_exempt
def ckfinder_api(request, *args, **kwargs):
    """
    ckfinder api
    :param request:
    :return:
    """

    # 获取配置
    ckfinder_server_settings = CkfinderFieldSettings.get_server_settings()

    # 自定义用户解析方法
    get_user_fun_str = ckfinder_server_settings.get('get_user_fun', '')
    get_user_fun = load_object(get_user_fun_str) if get_user_fun_str else None

    if get_user_fun and isfunction(get_user_fun):
        user = get_user_fun(request, *args, **kwargs)
        if user and user.is_authenticated:
            request.user = user

    # 实例化 Ckfinder
    _ckfinder = Ckfinder(request.GET, request.POST, __get_file(request), ckfinder_server_settings)

    # 获取存储资源
    resource_config = CkfinderResource.objects.filter(enabled=True).all()

    if resource_config:
        # 获取当前用户所有权限
        all_permissions = request.user.get_all_permissions()

        # 判断权限并设置用户可访问的存储资源
        for i in resource_config:
            _ckfinder.add_resource(**i.get_resource()).add_rule(i.get_rule(all_permissions))

    return __get_response(response_data=_ckfinder.run())
