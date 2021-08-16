# -*- coding: utf-8 -*-
#
# 同步模型相关
#
# django 常用导入
# =========================================
import json
from hashlib import md5

from framework.utils import trace_msg

try:
    import cPickle as pickle
except ImportError:
    import pickle
import requests
from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render

from framework.route import Route
from framework.views import notauth

from django.apps import apps
from .models import SyncModel, SyncModelMap
from framework.utils import import_module_attr

# ==========================================

_MODULES = SyncModelMap

_AUTHKEY = '122333444455555$'


def get_model_class(model_id):
    # 旧的方式,数字获取
    if str(model_id).isalnum():
        return import_module_attr(_MODULES.get(model_id))
    else:
        # 新的方式获取模型class
        return import_module_attr(model_id)

def get_old_model_id(backsData, model_id):
    if backsData['is_old']:
        for k, v in SyncModelMap.items():
            if v == model_id:
                return k


@notauth
@Route('sync/backstage/list')
@Route('sync/backstage/')
def backstage_list(request):
    form_operation = request.method
    operation_info = getattr(request, form_operation, None)
    model_id = None
    backs_id = None
    if operation_info:
        error_msg = ''
        model_id = operation_info.get('Modelid', '')
        backs_id = operation_info.get('Servid', '')  # 接收到字符串形式的若干id值
        is_remote = int(operation_info.get('is_remote', 0))  # 远程获取其他后台数据标识
        db_list = None
        if is_remote:
            backsData = get_backstage_data(bid=backs_id)
            back_url = backsData['url'] + 'sync/backstage/'
            model_id = get_old_model_id(backsData,model_id)

            try:
                response = requests.get(back_url, {"Modelid": model_id, "Servid": backs_id},
                                        timeout=60).content
                return HttpResponse(response)
            except:
                error_msg = "请求失败." + trace_msg()
                print(trace_msg())
        else:

            model = get_model_class(model_id)
            if model_id:
                db_list = model.objects.using('read').all().order_by('-id')
            else:
                error_msg = "请求失败."

        return render(request, 'sync_model/sync_backstage_push.html', {'db_list': db_list, 'error': error_msg})

    serv_list = get_backstage_data()

    model_list = {}

    for model_class in apps.get_models():
        key = '%s.%s' % (model_class.__module__, model_class.__name__)
        model_list[key] = model_class._meta.db_table

    results = {}
    results['model_id'] = model_id
    results['backs_id'] = backs_id
    results['serv_list'] = serv_list
    results['model_list'] = model_list

    return render(request, "sync_model/sync_backstage_list.html", results)


@Route('sync/backstage/edit')
def backstage_edit(request):
    sync_id = int(request.GET.get('sync_id', '') or 0)
    # 是否通过编辑按钮进入
    if sync_id:
        model = SyncModel.objects.get(id=sync_id)
    else:
        model = SyncModel()

    is_post = True if request.POST else False  # 是否提交了数据
    if is_post:
        backstage_name = request.POST.get('bs_name', '')
        backstage_url = request.POST.get('url', '')
        backstage_key = request.POST.get('key', '')
        model.key = backstage_key
        model.name = backstage_name
        model.url = backstage_url
        model.is_old = True if request.POST.get('is_old', False) else False
        model.save()

    return render(request, "sync_model/sync_backstage_edit.html", {'data': model})


@Route('sync/backstage/remove')
def backstage_remove(request):
    sync_id = int(request.GET.get("sync_id", 0))
    is_del = True if sync_id else False

    # 删除操作
    if is_del:
        SyncModel.objects.filter(id=sync_id).delete()
    return render(request, 'framework/feedback.html', locals())


@Route('sync/backstage/push')
def backstage_push(request):
    model_id = request.GET.get('Modelid', 0)
    serv_id = int(request.GET.get('Servid', 0))
    push_id = int(request.GET.get('Pushid', 0))
    is_local = int(request.GET.get('is_local', 0))  # 本地同步标识

    syncMod = get_model_class(model_id)  # 根据传入的model_id获取数据模型

    if not syncMod or not serv_id or not push_id:
        return HttpResponse('{"code": 1, "msg": "缺少请求所需参数"}')

    serv_info = get_backstage_data(bid=serv_id)

    serv_url = serv_info['url']
    if not serv_url:
        return HttpResponse('{"code": 1, "msg": "访问地址不存在"}')

    if is_local:
        # 从指定后台获取数据同步至本地
        url = serv_url + 'sync/backstage/remotedb'
        model_id = get_old_model_id(serv_info, model_id)
        post_data = {"Modelid": model_id, "Pushid": push_id}
        serialize_data = requests.post(url, data=post_data).content

        deserialize_data = json.loads(serialize_data)
        for model_config in deserialize_data:
            field_config = model_config['fields']
            field_config['id'] = model_config['pk']
            m = syncMod()
            m.set_attrs_for_dict(field_config)
            m.save()
        # sync_mods = deserialize('json', serialize_data)
        #
        #
        # for m in sync_mods:
        #     m.save()
        result = '{"code": 0}'
    else:
        # 本地数据推送至其他后台
        push_db = syncMod.objects.filter(id=push_id)  # 获取推送数据
        # post_datas = json.dumps(push_db)
        post_datas = serialize('json', push_db)
        hashObj = md5()
        hashObj.update(
                post_datas.encode(encoding='utf-8') + model_id.encode(encoding='utf-8') + _AUTHKEY.encode(
                        encoding='utf-8'))

        # 序列化模型和数据
        post_params = {'model': model_id, 'datas': post_datas, 'sign': hashObj.hexdigest()}

        try:
            result = requests.post(serv_url + 'sync/backstage/dosync', post_params, timeout=60).content

        except Exception as e:
            return HttpResponse('{"code": 1, "msg": "http_post: %s"}' % e)

    return HttpResponse(result)


@notauth
@Route('sync/backstage/dosync')
def do_backstage_sync(request):
    model_id = request.POST.get('model', None)
    datas = request.POST.get('datas', None)
    recept_auth = request.POST.get('sign', None)
    is_success = True
    error_msg = ''

    hashObj = md5()
    hashObj.update(
            datas.encode(encoding='utf-8') + model_id.encode(encoding='utf-8') + _AUTHKEY.encode(encoding='utf-8'))

    if str(recept_auth) == str(hashObj.hexdigest()):
        try:
            syncMod = get_model_class(model_id)
            deserialize_data = json.loads(datas)
            for model_config in deserialize_data:
                field_config = model_config['fields']
                field_config['id'] = model_config['pk']
                m = syncMod()
                m.set_attrs_for_dict(field_config)
                m.save()
        except Exception as e:
            error_msg = str(e)
            is_success = False
    else:
        error_msg = "auth key is invalid"
        is_success = False

    responseTxt = {'code': 0 if is_success else 1, 'msg': error_msg}
    return HttpResponse(json.dumps(responseTxt))


@notauth
@Route('sync/backstage/remotedb')
def get_remote_push_data(request):
    model_id = request.POST.get('Modelid', 0)
    push_id = int(request.POST.get('Pushid', 0))

    syncMod = get_model_class(model_id)

    push_db = syncMod.objects.filter(id=push_id)
    ret_data = serialize('json', push_db)

    return HttpResponse(ret_data)


# 自定义函数
def get_backstage_data(bid=0):
    if bid:
        return SyncModel.objects.filter(id=bid).values().first()
    else:
        return SyncModel.objects.values()
